# ETS Facturación Electrónica Panamá - HKA

Módulo de Odoo 18 para facturación electrónica en Panamá mediante integración con **The Factory HKA Corp**.

**Autor:** Easytech Services  
**Web:** https://easytechservices.com  
**Licencia:** LGPL-3

---

## Descripción

Permite emitir facturas electrónicas válidas ante la DGI (Dirección General de Ingresos) usando la API de HKA Factory: envío, CUFE, anulación y descarga de XML/PDF.

## Características

- Configuración de credenciales HKA por compañía (ambiente demo/producción)
- Envío de facturas y notas de crédito/débito a la DGI
- Obtención de CUFE y descarga de XML/PDF autorizados
- **Anulación en DGI** mediante wizard (motivo + confirmación)
- Consulta de estado y historial de documentos (hka.document)
- Códigos de ubicación Panamá (CSV), catálogo CPBS, unidades de medida
- Validación RUC y código de ubicación para contribuyentes
- Envío automático opcional al validar la factura

## Requisitos

- Odoo 18
- Cuenta activa en The Factory HKA
- Licencia de facturación electrónica vigente
- Certificado digital (producción)
- Python: `requests`, `PyJWT`

## Instalación

1. Añadir la carpeta del módulo a la ruta de addons de Odoo.
2. Actualizar lista de aplicaciones.
3. Buscar **"ETS Facturación Electrónica Panamá - HKA"** e instalar.

## Uso básico

- **Enviar a DGI:** En la factura validada, botón *Enviar a DGI*.
- **Anular en DGI:** Botón *Anular en DGI* → indicar motivo → Confirmar (solo si está autorizada y sin nota de crédito asociada).
- **Ubicaciones:** Carga desde `data/hka_ubicaciones.csv` (formato P-D-C según catálogo DGI/HKA).

## Versión

18.0.1.1.0
