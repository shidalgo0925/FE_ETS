# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Según catálogos HKA (tipoClienteFE)
    pa_tipo_cliente_fe = fields.Selection(
        [
            ('01', 'Contribuyente'),
            ('02', 'Consumidor Final'),
            ('03', 'Gobierno'),
            ('04', 'Extranjero'),
        ],
        string='Tipo cliente FE',
        default='02',
    )
    pa_ruc = fields.Char(string='RUC (Panamá)')
    # Según catálogos HKA (tipoContribuyente)
    pa_tipo_ruc = fields.Selection(
        [
            ('1', 'Natural'),
            ('2', 'Jurídico'),
        ],
        string='Tipo contribuyente',
        default='2',
    )
    pa_dv = fields.Char(string='Dígito verificador RUC')
    pa_corregimiento = fields.Char(string='Corregimiento')
    pa_codigo_ubicacion = fields.Char(string='Código ubicación (legacy)')
    hka_codigo_ubicacion = fields.Char(string='Código ubicación (texto libre)')
    pa_codigo_ubicacion_id = fields.Many2one(
        'hka.codigo.ubicacion',
        string='Código ubicación P-D-C',
        ondelete='set null',
    )
    # Lectura desde catálogo (solo informativo en formulario)
    pa_fe_provincia = fields.Char(
        related='pa_codigo_ubicacion_id.provincia',
        string='Provincia (catálogo)',
        readonly=True,
    )
    pa_fe_distrito = fields.Char(
        related='pa_codigo_ubicacion_id.distrito',
        string='Distrito (catálogo)',
        readonly=True,
    )
    pa_fe_corregimiento = fields.Char(
        related='pa_codigo_ubicacion_id.corregimiento',
        string='Corregimiento (catálogo)',
        readonly=True,
    )

    @api.model
    def _sync_vals_from_ubicacion_catalog(self, vals):
        """Al elegir una fila del catálogo DGI/HKA, alinea código y corregimiento para el API."""
        ub_id = vals.get('pa_codigo_ubicacion_id')
        if ub_id:
            Ub = self.env['hka.codigo.ubicacion']
            ub = Ub.browse(ub_id)
            if ub.exists():
                vals['hka_codigo_ubicacion'] = ub.codigo or False
                vals['pa_corregimiento'] = ub.corregimiento or False
        elif vals.get('pa_codigo_ubicacion_id') is False:
            vals.setdefault('hka_codigo_ubicacion', False)
            vals.setdefault('pa_corregimiento', False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._sync_vals_from_ubicacion_catalog(vals)
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        if 'pa_codigo_ubicacion_id' in vals:
            self._sync_vals_from_ubicacion_catalog(vals)
        return super().write(vals)

    def action_hka_ubicacion_help(self):
        """Documentación HKA Factory (método Enviar, cliente / codigoUbicación)."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://felwiki.thefactoryhka.com.pa/enviar',
            'target': 'new',
        }
