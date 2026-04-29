# Instalación — FE_ETS (Panamá) / Odoo 19

> **No use** *Aplicaciones → Importar módulo* con un ZIP. Vea `LEEME_INSTALACION.txt` y el comentario en el código de Odoo: los módulos “importados” **no cargan Python**; este addon **debe** ir en el sistema de archivos del servidor (`addons_path`).

Módulo técnico: **FE_ETS** (carpeta del addon; el nombre en Apps es *FE_ETS (Panamá)*).

## 1. Requisitos

| Requisito | Notas |
|-----------|--------|
| **Odoo 19** | Misma base de código y entorno que el resto de la instancia. |
| **PostgreSQL** | Base de datos ya creada para Odoo. |
| **Python 3** | Mismo intérprete del servicio Odoo. |
| **Módulos Odoo** | `base`, `product`, `account`, `contacts` (dependencias del manifiesto). |

### Dependencias Python (declaradas en el manifiesto)

Instalar en el entorno virtual de Odoo, por ejemplo:

```bash
# Ajuste la ruta al venv de su instalación Odoo 19
/path/to/odoo19-venv/bin/pip install requests PyJWT qrcode
```

Reiniciar el servicio de Odoo tras instalar paquetes.

## 2. Instalar el código del addon

**No importe el ZIP con “Aplicaciones → Importar módulo”.** Ese asistente no carga archivos `.py`; fallará en `ir.model.access` porque los modelos no existen. Descomprima el ZIP (o clone el repo) en el **sistema de archivos** del servidor y use `addons_path` como abajo.

1. Copie o despliegue la carpeta del módulo en el servidor, por ejemplo:

   `/opt/ETS/odoo19/custom-addons/fe_panama/FE_ETS`

2. Asegure permisos de lectura para el usuario que ejecuta Odoo (p. ej. `odoo19`).

3. Incluya la ruta del **directorio padre** (o el path concreto) en **`addons_path`** del fichero de configuración de Odoo, por ejemplo `odoo19.conf`:

   ```ini
   addons_path = /ruta/odoo/addons,/opt/ETS/odoo19/custom-addons/fe_panama
   ```

   (La carpeta listada debe ser la que **contiene** el directorio `FE_ETS`, no el `addons` de Odoo core a menos que usted ponga el addon allí.)

4. Reinicie Odoo.

## 3. Instalar el módulo en la base de datos

### Desde la interfaz (recomendado)

1. Activa el **modo desarrollador** (si aplica).
2. **Aplicaciones** → quitar el filtro “Aplicaciones” y buscar **FE_ETS** o *FE_ETS (Panamá)*.
3. **Actualizar lista de aplicaciones**.
4. Instalar el módulo.

### Desde línea de comandos (ejemplo)

Ajuste `-c`, base de datos, usuario y ruta a `odoo-bin` según su entorno. Si el puerto HTTP 8072 ya está en uso por otra instancia, use un puerto libre (p. ej. 8099) solo para este comando:

```bash
sudo -u odoo19 /path/to/odoo-bin -c /etc/odoo/odoo19.conf -d NOMBRE_BD -i FE_ETS --stop-after-init --http-port=8099
```

### Si ya tenía instalado `FE_HKA_OCI` (mismo código, nombre antiguo)

Tras renombrar la carpeta a **FE_ETS**, la base de datos puede seguir registrando el módulo como
`fe_hka_oci`. Antes de arrancar Odoo, en **PostgreSQL** (ajuste el nombre de la base):

```sql
UPDATE ir_module_module SET name = 'fe_ets' WHERE name = 'fe_hka_oci';
UPDATE ir_model_data SET module = 'fe_ets' WHERE module = 'fe_hka_oci';
```

Haga copia de seguridad de la base antes. Reinicie Odoo y actualice el módulo **FE_ETS** desde Apps
(o `-u FE_ETS`). Si prefiere una instalación limpia, desinstale el módulo antiguo en un entorno de
prueba antes (no recomendado en producción sin plan de migración).

## 4. Tras instalar: datos y hook

- **Ubicaciones DGI (contactos / receptor):** el catálogo **P–D–C** (provincia–distrito–corregimiento) se carga desde `data/hka_ubicaciones.csv` (cientos de filas, alineado al catálogo unificado de referencia DGI) mediante el hook **`post_init`**. Tras **actualizar** el módulo a la versión que incorpora el CSV ampliado, la migración `migrations/19.0.1.6.0/post-reload_ubicaciones_dgi` vuelve a fusionar esos datos.
- Si faltan filas o el CSV no se encuentra, revise el log del servicio Odoo (mensajes `FE_ETS:`).
- **CPBS** y **unidades de medida** siguen viniendo de los XML en `data/`.

## 5. Actualizar el módulo (código nuevo en disco)

1. Sustituya o actualice los archivos en `FE_ETS`.
2. **Aplicaciones** → *Actualizar lista* → en el módulo: **Actualizar**  
   o:

   ```bash
   sudo -u odoo19 /path/to/odoo-bin -c /etc/odoo/odoo19.conf -d NOMBRE_BD -u FE_ETS --stop-after-init --http-port=8099
   ```

## 6. Configuración operativa (resumen)

1. **Ajustes → Empresas → [Su empresa] →** pestaña **FE_ETS (Panamá)**:  
   - Ambiente, usuario y contraseña del **PAC** (servicio de facturación electrónica).  
   - RUC emisor, DV, sucursal, punto de facturación, CAFE, etc.  
   - Use **Probar conexión** cuando el PAC lo permita.
2. **Contactos (Panamá):** tipo de cliente FE, RUC/DV si aplica, **código de ubicación P–D–C** desde el catálogo.
3. **Productos / categorías:** **CPBS** y **unidad DGI (FE)** donde corresponda.
4. **Facturas de venta:** validar y **Enviar a DGI** (o activar envío automático en empresa si lo desea).

## 7. Red y acceso

- Compruebe en qué **puerto HTTP** escucha esta instancia Odoo 19 (p. ej. 8072) y use esa URL, no otra (p. ej. 8069 si es Odoo 18 en el mismo host).
- El **longpolling** (chat/bus) usa otro puerto si lo tiene configurado.

## 8. Problemas frecuentes

| Síntoma | Qué revisar |
|---------|-------------|
| El módulo no aparece en Apps | Ruta en `addons_path`, permisos, **Actualizar lista de aplicaciones**. |
| Error al instalar: dependencia Python | `pip` en el **mismo** venv del servicio; reiniciar Odoo. |
| `Access Denied` o módulo no carga | Usuario de sistema o grupo Odoo adecuado, logs `journalctl` / logfile de Odoo. |
| Secuencia o datos XML no se renombran tras update | Algunos registros tienen `noupdate="1"`; renombre manual en **Técnico** si aplica. |

## 9. Licencia y aviso

El manifiesto declara la licencia **Other proprietary** (software propietario; detalle en `__manifest__.py`). La documentación y catálogos DGI pueden variar. Verifique siempre requisitos vigentes ante la **DGI** y su **PAC**.

---

*Documento generado para el addon FE_ETS — versión de referencia en `__manifest__.py` (`version`).*
