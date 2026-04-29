# Licenciamiento FE_ETS - Fase 1 - Dia 4

## Objetivo

Aplicar validacion de licencia con cache/gracia y guardas en funciones criticas sin romper Odoo.

## Implementado

### 1) Cache + gracia en `res.company`

Archivo: `models/res_company.py`

- Nuevo campo: `hka_license_grace_hours`
- Helper de staleness: `_is_license_check_stale(max_age_hours=12)`
- Activacion de gracia por caida del servidor: `_activate_grace_mode_if_possible(...)`
- Metodo central de enforcement: `ensure_hka_license_allows_operation(operation_name)`
  - Revalida licencia si esta desactualizada o en estado desconocido/invalido.
  - Si hay error de conectividad, intenta modo gracia.
  - Bloquea con mensaje claro en estados `expired/suspended/invalid`.

### 2) Guardas en operaciones criticas

Archivo: `models/account_move.py`

- `action_send_hka` -> valida licencia antes de enviar.
- `action_cancel_dgi` -> valida licencia antes de anular.
- `action_reprint_fiscal` -> valida licencia antes de descargar.

Archivo: `models/hka_document.py`

- `action_download_xml` y `action_download_pdf` -> valida licencia.
- `action_check_status` -> valida licencia.
- `_download_from_hka` y `action_check_status` ahora usan `company._get_hka_client()` (respeta modo `direct_hka` o `ets_api`).

## Prueba rapida ejecutada

En DB `pr2`:

1. `ETS-VALID-001` -> `ensure_hka_license_allows_operation(...)` permitido, estado `active`.
2. `ETS-NOPE-001` -> bloquea con mensaje "Licencia invalida...".

## Resultado

El flujo queda controlado por licencia, con bloqueo correcto y sin afectar estabilidad del sistema.
