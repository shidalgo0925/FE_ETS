# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HKACodigoUbicacion(models.Model):
    """Catálogo unificado Provincia–Distrito–Corregimiento (código P-D-C), alineado a DGI / HKA Factory.

    El listado en pantalla replica el criterio del catálogo: una línea por combinación
    ``Provincia, Distrito, Corregimiento`` (como en el portal / documentación HKA).
    """
    _name = 'hka.codigo.ubicacion'
    _description = 'Código ubicación DGI (Panamá)'
    _order = 'provincia, distrito, corregimiento, codigo'
    _rec_name = 'codigo'
    _rec_names_search = ['codigo', 'provincia', 'distrito', 'corregimiento']

    codigo = fields.Char(required=True, index=True)
    provincia = fields.Char()
    distrito = fields.Char()
    corregimiento = fields.Char()
    activo = fields.Boolean(default=True)

    @api.depends('codigo', 'provincia', 'distrito', 'corregimiento')
    def _compute_display_name(self):
        for rec in self:
            parts = [p for p in (rec.provincia, rec.distrito, rec.corregimiento) if p]
            geo = ', '.join(parts) if parts else ''
            code = (rec.codigo or '').strip()
            # Mismo formato que listados tipo portal: "Provincia, Distrito, Corregimiento"
            if geo:
                rec.display_name = geo
            elif code:
                rec.display_name = code
            else:
                rec.display_name = f'{rec._name},{rec.id}'
