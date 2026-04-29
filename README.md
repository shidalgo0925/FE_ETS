# FE_ETS (Panamá) — HKA

Módulo de **Odoo 18** para emitir facturas electrónicas en Panamá integrado con **The Factory HKA Corp** (proveedor autorizado ante la DGI).

| | |
|---|---|
| **Autor** | Easy Technology Services |
| **Web** | https://easytech.services |
| **Repositorio** | https://github.com/shidalgo0925/FE_ETS |
| **Licencia** | Other proprietary |
| **Versión** | 18.0.1.1.0 |
| **Última actualización** | Marzo 2026 |

---

## ¿Qué hace este módulo?

- Conecta Odoo con la API de HKA para enviar facturas y notas de crédito/débito a la **DGI (Dirección General de Ingresos)**.
- Obtiene el **CUFE** (Código Único de Factura Electrónica), descarga el **XML y PDF** autorizados y permite **anular** documentos ya autorizados desde Odoo.
- Gestiona **códigos de ubicación** de Panamá (provincia, distrito, corregimiento), **CPBS** y validación de **RUC** para contribuyentes.

## Características

- **Configuración:** Credenciales HKA por compañía (demo/producción), envío automático opcional al validar.
- **Envío a DGI:** Botón *Enviar a DGI* en facturas y notas de crédito/débito validadas.
- **Anulación:** Botón *Anular en DGI* → wizard para indicar motivo → solo si la factura está autorizada y no tiene nota de crédito asociada.
- **Documentos:** Historial en *FE_ETS* / documento electrónico (CUFE, estado, PDF) según pantallas del módulo.
- **Ubicaciones:** Carga desde CSV (`data/hka_ubicaciones.csv`) según catálogo DGI/HKA; una sola fuente para evitar errores de código.
- **Contactos:** Tipo de cliente (contribuyente/consumidor final), RUC y código de ubicación para FE.

## Requisitos

- **Odoo:** 18.0
- **Python:** `requests`, `PyJWT`
- **HKA:** Cuenta activa en The Factory HKA, licencia de facturación electrónica vigente; certificado digital para producción.

## Instalación

**Paquete ZIP (solo para copiar al servidor):**  
https://github.com/shidalgo0925/FE_ETS/raw/main/FE_ETS_Odoo19.zip  

**Prohibido:** *Aplicaciones → Importar módulo* con el ZIP. Odoo **no registra el código Python** de esos paquetes; fallarán datos y vistas que usan `hka.*`. Lea **`LEEME_INSTALACION.txt`** en la raíz del módulo.

**Instalación correcta:** descomprimir el ZIP en el **servidor** en una ruta de `addons_path`, **reiniciar Odoo**, *Actualizar lista de aplicaciones* e instalar **FE_ETS (Panamá)** (búsqueda: FE_ETS).

1. Carpeta `FE_ETS` accesible en `addons_path` (debe existir `FE_ETS/__manifest__.py`).
2. Reiniciar el servicio Odoo.
3. **Apps** → actualizar lista → instalar el módulo.

## Uso rápido

- **Enviar una factura:** Validar la factura → botón *Enviar a DGI*. Si está activo el envío automático, se envía al validar.
- **Anular en DGI:** Solo para facturas ya autorizadas. Botón *Anular en DGI* → escribir motivo (opcional) → *Confirmar*.
- **Reimprimir PDF fiscal:** Botón *Reimprimir factura fiscal* una vez enviada.

## Estructura del repositorio

- `models/` — account_move, hka_api, hka_document (envío, anulación, descarga).
- `wizard/` — wizard de anulación en DGI (motivo + confirmar).
- `data/` — carga de ubicaciones Panamá (CSV), secuencias, CPBS, etc.
- `views/` — formularios y botones de factura, documentos FE, contactos, configuración.

## Dónde encontrarnos

- **Soporte y contacto:** [Easy Technology Services](https://easytech.services)
- **Código fuente:** [GitHub – FE_ETS](https://github.com/shidalgo0925/FE_ETS)
- **Odoo 19** · FE Panamá · The Factory HKA · DGI

---

Desarrollado por **Easy Technology Services** · https://easytech.services
