# Checklist salida a produccion - FE_ETS

## Pre-despliegue

- [ ] Backup de base de datos realizado
- [ ] Ruta addons cliente creada (`.../custom-addons/modecosa`)
- [ ] `addons_path` actualizado y verificado
- [ ] Dependencias Python instaladas (`requests`, `PyJWT`, `qrcode`)

## Despliegue

- [ ] Carpeta `FE_ETS` desplegada
- [ ] Permisos `odoo:odoo` aplicados
- [ ] Servicio `odoo19` reiniciado
- [ ] Modulo FE_ETS instalado/actualizado desde Apps

## Licenciamiento

- [ ] Codigo de licencia cargado
- [ ] URL servidor licencias configurada
- [ ] Token servidor licencias configurado (si aplica)
- [ ] Boton `Activar licencia` ejecutado
- [ ] Estado en `Activa`

## Pruebas operativas minimas

- [ ] Prueba de conexion FE (boton Probar conexion)
- [ ] Envio de factura de prueba
- [ ] Descarga PDF/XML fiscal
- [ ] Validacion de bloqueo con licencia invalida (entorno controlado)

## Cierre

- [ ] Manual entregado al operador tecnico
- [ ] Evidencias de pruebas guardadas
- [ ] Plan de rollback documentado
