# Manual tecnico - Instalacion y activacion FE_ETS

## 1. Instalacion del modulo (servidor)

1. Copiar carpeta `FE_ETS` en addons path de cliente:
   - Recomendado: `/opt/ETS/odoo19/custom-addons/modecosa/FE_ETS`
2. Verificar `addons_path` en `/etc/odoo/odoo19.conf` incluya:
   - `/opt/ETS/odoo19/custom-addons/modecosa`
3. Permisos:
   - `chown -R odoo:odoo /opt/ETS/odoo19/custom-addons/modecosa/FE_ETS`
4. Reiniciar Odoo:
   - `systemctl restart odoo19.service`
5. En Odoo:
   - Aplicaciones -> Actualizar lista de aplicaciones
   - Instalar/Actualizar `FE_ETS`

## 2. Activacion de licencia

1. Ir a:
   - Ajustes -> Empresas -> [Empresa]
   - Pestaña `FE_ETS (Panamá)` -> grupo `Licencia`
2. Configurar:
   - `Codigo de licencia`
   - `URL servidor licencias` (ej. `https://licencias.ets.com`)
   - `Token servidor licencias` (si aplica)
3. Pulsar:
   - `Activar licencia`
4. Validar estado:
   - Badge `Estado`: `Activa` (verde)
   - Mensaje y fecha de ultima validacion

## 3. Modos de integracion FE

En el mismo formulario de empresa:

- `Directo HKA (actual)` -> Odoo consume PAC directo
- `API ETS externa (opción 2)` -> Odoo prepara y delega ejecucion en backend ETS

## 4. Comportamiento ante licencia no valida

Si licencia `expired`, `suspended` o `invalid`, se bloquea:

- Envio a DGI
- Anulacion en DGI
- Descarga XML/PDF fiscal
- Consulta de estado (flujo FE)

## 5. Modo gracia

Si servidor de licencias no responde y habia estado valido previo:

- FE_ETS permite operacion temporal en `grace`
- Usa ventana de horas configurada (`hka_license_grace_hours`)

## 6. Soporte

Si aparece bloqueo por licencia:

1. Revalidar licencia desde empresa.
2. Verificar conectividad a URL de licencias.
3. Confirmar codigo/licencia vigente con soporte ETS.
