# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hka_unidad_medida_id = fields.Many2one(
        'hka.unidad.medida',
        string='Unidad DGI (FE)',
        ondelete='set null',
    )
    hka_cpbs_id = fields.Many2one(
        'hka.cpbs',
        string='CPBS',
        ondelete='set null',
    )
