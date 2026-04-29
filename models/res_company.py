# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    hka_usuario = fields.Char(string='Usuario del servicio (PAC)')
    hka_clave = fields.Char(string='Contraseña del servicio')
    hka_ambiente = fields.Selection(
        [('demo', 'Demo / Pruebas'), ('production', 'Producción')],
        string='Ambiente',
        default='demo',
    )
    hka_ruc = fields.Char(string='RUC emisor (DGI)')
    hka_dv = fields.Char(string='DV (emisor)')
    hka_punto_facturacion = fields.Char(string='Punto de facturación', default='001')
    hka_codigo_sucursal = fields.Char(string='Código sucursal', default='0000')
    hka_tipo_sucursal = fields.Selection(
        [
            ('1', 'Principal'),
            ('2', 'Secundaria'),
        ],
        string='Tipo sucursal',
        default='1',
    )
    hka_formato_cafe = fields.Selection(
        [
            ('1', 'Sin generación de CAFE'),
            ('2', 'Imagen'),
            ('3', 'Papel formato carta'),
        ],
        string='Formato CAFE',
        default='2',
    )
    hka_entrega_cafe = fields.Selection(
        [
            ('1', 'Sin generación de CAFE'),
            ('2', 'CAFE en papel al receptor'),
            ('3', 'Email'),
        ],
        string='Entrega CAFE',
        default='3',
    )
    hka_auto_send = fields.Boolean(
        string='Enviar automáticamente al confirmar factura',
        default=False,
    )
    hka_numero_licencia = fields.Char(string='Número de licencia')
    hka_folios_disponibles = fields.Integer(
        string='Folios disponibles',
        default=0,
    )
    hka_ultima_sincronizacion = fields.Datetime(string='Última sincronización')

    def action_hka_test_connection(self):
        """Prueba usuario/clave contra la API de autenticación HKA."""
        self.ensure_one()
        if not self.hka_usuario or not self.hka_clave:
            raise UserError(_('Indique usuario y contraseña del servicio de facturación.'))
        from .hka_api import HKAApiClient
        client = HKAApiClient(
            self.hka_usuario,
            self.hka_clave,
            self.hka_ambiente or 'demo',
        )
        res = client.authenticate()
        if res.get('success'):
            self.sudo().write({
                'hka_ultima_sincronizacion': fields.Datetime.now(),
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Conexión al servicio'),
                    'message': _('Autenticación correcta con el PAC (%s).') % (self.hka_ambiente or 'demo'),
                    'type': 'success',
                    'sticky': False,
                },
            }
        raise UserError(_('No se pudo conectar con el servicio de facturación: %s') % (res.get('error') or _('Error desconocido')))
