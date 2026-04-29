# -*- coding: utf-8 -*-
{
    'name': 'Facturación Electrónica de ETS',
    'version': '19.0.1.6.5',
    'category': 'Accounting/Localizations/EDI',
    'summary': (
        'Odoo 19: facturación electrónica Panamá (DGI) — emisión, envío y seguimiento de '
        'comprobantes con Easy Technology Services.'
    ),
    'description': """
Facturación Electrónica de ETS (Odoo 19 - Panamá)
=================================================

**Qué es este módulo**

Localización operativa para **facturación electrónica** en **Panamá**, enlazando **Odoo 19**
con un **proveedor autorizado de certificación (PAC)** y los requisitos de la
**Dirección General de Ingresos (DGI)** y los catálogos oficiales aplicables.

El **nombre técnico** del módulo en Odoo es **FE_ETS** (debe coincidir con el nombre de la
carpeta del addon en ``addons_path``). La instalación correcta y el aviso sobre *Importar módulo
(ZIP)* están en ``LEEME_INSTALACION.txt`` en el addon.

**Funcionalidades principales**

* **Empresa (res.company):** credenciales y ambiente del servicio de facturación, datos del
  emisor (RUC, dígito verificador, sucursal), formato y entrega CAFE, licencia/folios si aplica,
  prueba de conexión con el PAC.
* **Contactos (res.partner):** tipo de cliente FE (contribuyente, consumidor final, gobierno,
  extranjero), RUC y DV, selección de **código de ubicación P-D-C** desde catálogo alineado a la
  normativa DGI, datos de ubicación fiscal para armado del receptor en el documento electrónico.
* **Catálogos:** códigos **Provincia-Distrito-Corregimiento**, **CPBS** (clasificación de bienes
  y servicios) y **unidades de medida** según tablas de referencia usadas en la integración;
  datos iniciales incluidos en el módulo y ampliables desde Odoo.
* **Productos:** plantillas y categorías con **CPBS** y **unidad homologada para FE** para cumplir
  validaciones al armar líneas de factura (incl. reglas de ítems y tributación aplicables según
  configuración).
* **Facturas / asientos (account.move):** preparación del envío al PAC, recepción de respuesta
  (código, mensaje, CUFE/QR cuando aplique), flujos de error orientativos y utilidades
  relacionadas con cancelación según lo implementado en el addon.

**Dependencias técnicas (Python)**

``requests``, ``PyJWT``, ``qrcode`` (declaradas en ``external_dependencies``).

**Autor y licencia del software**

* **Autor / titular:** **Easy Technology Services**.
* **Licencia (manifiesto Odoo):** el campo ``license`` usa el valor estándar **Other proprietary**;
  en la ficha del módulo, **Autor** mostrará *Easy Technology Services*. Las condiciones de uso
  del software son propietarias.
* **Alcance:** el uso, copia, modificación, descompilación, redistribución o sublicenciamiento
  quedan sujetos al acuerdo con **Easy Technology Services** y a la ley aplicable; no se otorgan
  derechos de código abierto salvo lo imperativamente exigido por ley.

**Propiedad intelectual y derechos de autor (Panamá)**

En los términos de la **Ley 64 de 19 de octubre de 1994**, por la cual se adopta el texto del
**Decreto Ley 261 de 1994** sobre derechos de autor y derechos conexos en Panamá, las obras
literarias y software se encuentran protegidas. **Easy Technology Services** se reserva todos los
derechos morales y patrimoniales que correspondan sobre este trabajo en la medida aplicable.

La denominación comercial **ETS**, documentación propia y elementos distintivos del presente
addon permanecen sujetos a la protección legal aplicable y a los términos de licencia
procedentes.

**Descargo**

Los catálogos oficiales (DGI), formatos de validación y respuestas del PAC pueden cambiar;
el usuario debe verificar siempre los requisitos vigentes ante **DGI** y ante su proveedor PAC.
""",
    'author': 'Easy Technology Services',
    'website': 'https://easytech.services',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'product',
        'account',
        'contacts',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/hka_codigo_ubicacion_views.xml',
        'views/hka_catalog_views.xml',
        'views/product_template_views.xml',
        'views/account_move_views.xml',
        'wizard/hka_cancel_wizard_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['requests', 'PyJWT', 'qrcode'],
    },
    'post_init_hook': 'load_panama_locations',
}
