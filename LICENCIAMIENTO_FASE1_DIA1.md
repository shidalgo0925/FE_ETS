# Licenciamiento FE_ETS - Fase 1 - Dia 1

Documento base para implementacion backend + Odoo sin suposiciones.

## 1) Contrato API definitivo

### Endpoint

- Metodo: `POST`
- URL: `/api/v1/license/validate`
- Auth: `Bearer <backend_api_token>` (recomendado para canal servidor-servidor)
- Timeout cliente Odoo: `5s`
- Reintentos: `3` (backoff simple: 1s, 2s, 4s)

### Request JSON

```json
{
  "license_key": "ETS-PRD-XXXX-XXXX-XXXX",
  "db_uuid": "a21c5f2a-5bc9-49f1-9f3f-0f7b1c6c4f98",
  "base_url": "https://cliente.com",
  "module_name": "FE_ETS",
  "module_version": "19.0.1.6.9",
  "company_vat": "155677155-2-2023",
  "instance_fingerprint": "sha256_hex(db_uuid|base_url|company_vat)"
}
```

### Response JSON (200)

```json
{
  "valid": true,
  "status": "active",
  "expires_at": "2026-12-31T23:59:59Z",
  "grace_hours": 72,
  "message": "Licencia activa",
  "error_code": null,
  "signature": "hmac_sha256_hex(payload_canonico, shared_secret)",
  "server_time": "2026-04-29T06:00:00Z"
}
```

### Status permitidos

- `active`
- `grace`
- `expired`
- `suspended`
- `invalid`

### Error codes normalizados

- `LIC_ACTIVE`
- `LIC_GRACE`
- `LIC_EXPIRED`
- `LIC_SUSPENDED`
- `LIC_INVALID`
- `LIC_NOT_FOUND`
- `LIC_FINGERPRINT_MISMATCH`
- `LIC_SERVER_DOWN`
- `LIC_SIGNATURE_INVALID`
- `LIC_BAD_REQUEST`

## 2) Reglas de negocio (bloqueo por estado)

Funciones criticas FE_ETS:

- `action_send_hka`
- `action_cancel_hka`
- `descargar_documento` / `action_reprint_fiscal`
- envio automatico (`_post` -> `action_send_hka`)

Matriz:

| Estado licencia | Enviar | Anular | Descargar | Autoenvio | Nota |
|---|---|---|---|---|---|
| `active` | Si | Si | Si | Si | Operacion normal |
| `grace` | Si | Si | Si | Si | Mostrar advertencia |
| `expired` | No | No | No | No | Bloqueo total de funciones criticas |
| `suspended` | No | No | No | No | Bloqueo total + mensaje soporte |
| `invalid` | No | No | No | No | Bloqueo total |

Regla de gracia:

- Si el servidor de licencias no responde y la ultima validacion fue `active`/`grace`, permitir operacion hasta `grace_hours`.
- Si supera `grace_hours`, pasar a bloqueo (`expired` logico por conectividad).

## 3) Mensajes de usuario + codigos

Mensajes UI recomendados:

- `LIC_ACTIVE`: "Licencia activa."
- `LIC_GRACE`: "Sin conexion con servidor de licencias. Operando en modo gracia (%s h restantes)."
- `LIC_EXPIRED`: "Licencia vencida. Contacte a soporte ETS para renovacion."
- `LIC_SUSPENDED`: "Licencia suspendida. Contacte a soporte ETS."
- `LIC_INVALID`: "Licencia invalida. Revise el codigo e intente nuevamente."
- `LIC_NOT_FOUND`: "Licencia no encontrada."
- `LIC_FINGERPRINT_MISMATCH`: "La licencia no corresponde a esta instancia."
- `LIC_SERVER_DOWN`: "No se pudo validar la licencia por conectividad. Reintentando."
- `LIC_SIGNATURE_INVALID`: "Respuesta de licenciamiento invalida. Contacte soporte."
- `LIC_BAD_REQUEST`: "Solicitud de validacion incompleta o invalida."

## 4) Criterio de hecho Dia 1

Se considera terminado Dia 1 cuando:

1. Backend y Odoo aceptan este mismo contrato JSON sin cambios.
2. Las reglas de bloqueo por estado quedan aprobadas.
3. Los codigos y mensajes UI quedan cerrados para implementacion Dia 2 y Dia 3.

## 5) Notas de implementacion para Dia 2+

- Verificar `signature` en Odoo antes de confiar en `valid/status`.
- Guardar `license_last_check`, `license_status`, `license_message`, `license_expires_at`.
- Registrar en logs cada validacion (request_id, estado, error_code, duracion).
