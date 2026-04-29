#!/usr/bin/env python3
"""Mock backend ETS para validacion de licencias (Dia 2).

Endpoint:
  POST /api/v1/license/validate
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


HOST = os.environ.get("ETS_LIC_HOST", "127.0.0.1")
PORT = int(os.environ.get("ETS_LIC_PORT", "8899"))
SHARED_SECRET = os.environ.get("ETS_LIC_SHARED_SECRET", "change-me")
API_TOKEN = os.environ.get("ETS_LIC_API_TOKEN", "dev-token")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _fingerprint(db_uuid: str, base_url: str, company_vat: str) -> str:
    raw = f"{db_uuid}|{base_url}|{company_vat}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _canonical_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sign(payload: dict[str, Any]) -> str:
    raw = _canonical_payload(payload).encode("utf-8")
    return hmac.new(SHARED_SECRET.encode("utf-8"), raw, hashlib.sha256).hexdigest()


def _load_licenses() -> dict[str, dict[str, Any]]:
    # Demo store (en producción vendria de DB)
    return {
        "ETS-VALID-001": {
            "status": "active",
            "expires_at": "2027-12-31T23:59:59Z",
            "grace_hours": 72,
            "bound_fingerprint": None,  # se liga en primer uso
        },
        "ETS-EXPIRED-001": {
            "status": "expired",
            "expires_at": "2024-12-31T23:59:59Z",
            "grace_hours": 72,
            "bound_fingerprint": None,
        },
        "ETS-SUSP-001": {
            "status": "suspended",
            "expires_at": "2027-12-31T23:59:59Z",
            "grace_hours": 0,
            "bound_fingerprint": None,
        },
    }


class LicenseHandler(BaseHTTPRequestHandler):
    server_version = "ETS-Lic-Server/0.1"

    def _json_response(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any] | None:
        try:
            content_len = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_len) if content_len else b"{}"
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                return None
            return data
        except Exception:
            return None

    def _auth_ok(self) -> bool:
        auth = self.headers.get("Authorization", "")
        return auth == f"Bearer {API_TOKEN}"

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/v1/license/validate":
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        if not self._auth_ok():
            self._json_response(
                HTTPStatus.UNAUTHORIZED,
                {"valid": False, "status": "invalid", "error_code": "LIC_BAD_REQUEST", "message": "Unauthorized"},
            )
            return

        data = self._read_json()
        if not data:
            self._json_response(
                HTTPStatus.BAD_REQUEST,
                {"valid": False, "status": "invalid", "error_code": "LIC_BAD_REQUEST", "message": "Invalid JSON"},
            )
            return

        required = ["license_key", "db_uuid", "base_url", "module_name", "module_version", "company_vat", "instance_fingerprint"]
        if any(not data.get(k) for k in required):
            self._json_response(
                HTTPStatus.BAD_REQUEST,
                {"valid": False, "status": "invalid", "error_code": "LIC_BAD_REQUEST", "message": "Missing required fields"},
            )
            return

        expected_fp = _fingerprint(data["db_uuid"], data["base_url"], data["company_vat"])
        if expected_fp != data["instance_fingerprint"]:
            resp = {
                "valid": False,
                "status": "invalid",
                "expires_at": None,
                "grace_hours": 0,
                "message": "Instance fingerprint mismatch",
                "error_code": "LIC_FINGERPRINT_MISMATCH",
                "server_time": _iso(_utc_now()),
            }
            resp["signature"] = _sign(resp)
            self._json_response(HTTPStatus.OK, resp)
            return

        licenses = _load_licenses()
        lic = licenses.get(data["license_key"])
        if not lic:
            resp = {
                "valid": False,
                "status": "invalid",
                "expires_at": None,
                "grace_hours": 0,
                "message": "License not found",
                "error_code": "LIC_NOT_FOUND",
                "server_time": _iso(_utc_now()),
            }
            resp["signature"] = _sign(resp)
            self._json_response(HTTPStatus.OK, resp)
            return

        # enlace fingerprint (simulado en memoria por request)
        bound = lic.get("bound_fingerprint")
        if bound and bound != data["instance_fingerprint"]:
            resp = {
                "valid": False,
                "status": "invalid",
                "expires_at": lic.get("expires_at"),
                "grace_hours": lic.get("grace_hours", 0),
                "message": "License belongs to another instance",
                "error_code": "LIC_FINGERPRINT_MISMATCH",
                "server_time": _iso(_utc_now()),
            }
            resp["signature"] = _sign(resp)
            self._json_response(HTTPStatus.OK, resp)
            return

        status = lic.get("status", "invalid")
        expires_at = lic.get("expires_at")
        exp_dt = _parse_iso(expires_at)
        if exp_dt and _utc_now() > exp_dt and status == "active":
            status = "expired"

        valid = status in {"active", "grace"}
        error_code = {
            "active": "LIC_ACTIVE",
            "grace": "LIC_GRACE",
            "expired": "LIC_EXPIRED",
            "suspended": "LIC_SUSPENDED",
            "invalid": "LIC_INVALID",
        }.get(status, "LIC_INVALID")
        message = {
            "active": "Licencia activa",
            "grace": "Licencia en modo gracia",
            "expired": "Licencia vencida",
            "suspended": "Licencia suspendida",
            "invalid": "Licencia invalida",
        }.get(status, "Licencia invalida")

        resp = {
            "valid": valid,
            "status": status,
            "expires_at": expires_at,
            "grace_hours": lic.get("grace_hours", 72),
            "message": message,
            "error_code": error_code,
            "server_time": _iso(_utc_now()),
        }
        resp["signature"] = _sign(resp)
        self._json_response(HTTPStatus.OK, resp)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", ""):
            self._json_response(
                HTTPStatus.OK,
                {
                    "service": "ETS mock license server",
                    "health": "/health",
                    "validate_endpoint": "/api/v1/license/validate",
                    "method": "POST",
                },
            )
            return
        if self.path == "/health":
            self._json_response(HTTPStatus.OK, {"ok": True, "service": "license", "time": _iso(_utc_now())})
            return
        self._json_response(HTTPStatus.NOT_FOUND, {"error": "Not found"})


def main() -> None:
    httpd = HTTPServer((HOST, PORT), LicenseHandler)
    print(f"ETS mock license server listening on http://{HOST}:{PORT}")
    print(f"Use Authorization: Bearer {API_TOKEN}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
