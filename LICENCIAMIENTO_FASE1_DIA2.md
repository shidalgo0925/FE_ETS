# Licenciamiento FE_ETS - Fase 1 - Dia 2

## Objetivo

Tener endpoint funcional de validacion de licencias para pruebas de integracion Odoo.

## Implementacion realizada

- Backend mock creado en:
  - `licensing_backend/mock_license_server.py`
- Documentacion de ejecucion:
  - `licensing_backend/README.md`
- Endpoint disponible:
  - `POST /api/v1/license/validate`

## Casos probados

1. Licencia valida (`ETS-VALID-001`) -> `valid=true`, `status=active`
2. Licencia invalida (`ETS-NOPE-001`) -> `valid=false`, `error_code=LIC_NOT_FOUND`
3. Licencia vencida (`ETS-EXPIRED-001`) -> `valid=false`, `status=expired`

## Criterio de hecho Dia 2

- Endpoint responde sin errores para los 3 casos base: valido, invalido, vencido.
- Contrato y codigos de respuesta compatibles con lo definido en Dia 1.

## Pendiente Dia 3

- Integrar campos/licencia UI en Odoo (empresa) y acciones de activacion/revalidacion.
