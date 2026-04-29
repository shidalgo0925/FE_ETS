# Licensing Backend (Mock) - Dia 2

Servidor mock para validar el contrato de licencias de Fase 1.

## Ejecutar

```bash
cd licensing_backend
python3 mock_license_server.py
```

Variables opcionales:

- `ETS_LIC_HOST` (default `127.0.0.1`)
- `ETS_LIC_PORT` (default `8899`)
- `ETS_LIC_API_TOKEN` (default `dev-token`)
- `ETS_LIC_SHARED_SECRET` (default `change-me`)

## Endpoint

- `POST /api/v1/license/validate`

Header:

```text
Authorization: Bearer dev-token
Content-Type: application/json
```

## Licencias demo incluidas

- `ETS-VALID-001` -> activa
- `ETS-EXPIRED-001` -> vencida
- `ETS-SUSP-001` -> suspendida

## Ejemplo request

```json
{
  "license_key": "ETS-VALID-001",
  "db_uuid": "a21c5f2a-5bc9-49f1-9f3f-0f7b1c6c4f98",
  "base_url": "https://cliente.com",
  "module_name": "FE_ETS",
  "module_version": "19.0.1.6.9",
  "company_vat": "155677155-2-2023",
  "instance_fingerprint": "sha256_hex(db_uuid|base_url|company_vat)"
}
```

## Nota

Este mock usa almacenamiento en memoria por simplicidad. En produccion debe conectarse a DB y registrar auditoria.
