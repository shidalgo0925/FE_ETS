# -*- coding: utf-8 -*-
from odoo import fields, models


class HKAUnidadMedida(models.Model):
    _name = 'hka.unidad.medida'
    _description = 'Unidad de medida DGI (FE)'
    _rec_name = 'name'

    name = fields.Char(required=True)
    code = fields.Char(string='Código', required=True, index=True)
