# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    hka_cpbs_id = fields.Many2one(
        'hka.cpbs',
        string='CPBS por defecto',
        ondelete='set null',
    )
