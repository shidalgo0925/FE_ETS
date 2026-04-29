# Licenciamiento FE_ETS - Fase 1 - Dia 5

## Objetivo

Validar escenarios clave y dejar paquete de entrega operable para soporte/implantacion.

## Matriz de pruebas ejecutada (DB: pr2)

| Caso | Resultado esperado | Resultado |
|---|---|---|
| Licencia valida (`ETS-VALID-001`) | Permite operacion | OK |
| Licencia invalida (`ETS-NOPE-001`) | Bloquea envio/operacion | OK |
| Licencia vencida (`ETS-EXPIRED-001`) | Bloquea | OK |
| Sin internet (backend caido) + estado previo valido | Permite en gracia | OK (forzado stale > 12h) |
| Reconexion backend | Vuelve a `active` | OK |

Notas:

- El modo gracia se activa al necesitar revalidacion (cache stale) y fallar conectividad.
- Se verifico activacion de gracia con `hka_license_last_check` forzado a 13h.

## Entregables finales

- Codigo FE_ETS con licenciamiento (Dia 1-4 + validaciones Dia 5)
- ZIP actualizado: `FE_ETS_Odoo19.zip`
- Manual instalacion + activacion: `MANUAL_INSTALACION_ACTIVACION_FE_ETS.md`
- Checklist operativo: `CHECKLIST_SALIDA_PRODUCCION_FE_ETS.md`

## Criterio de hecho Dia 5

1. Cliente tecnico puede instalar modulo sin tocar core de Odoo.
2. Cliente puede activar/revalidar licencia desde UI.
3. Funciones criticas quedan bloqueadas en estados no permitidos.
4. Sistema mantiene continuidad temporal con modo gracia en caida de servidor de licencias.
