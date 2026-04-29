# -*- coding: utf-8 -*-
from odoo import fields, models


class HKACPBS(models.Model):
    _name = 'hka.cpbs'
    _description = 'Código CPBS (DGI Panamá)'
    _rec_name = 'name'

    name = fields.Char(required=True)
    code = fields.Char(
        string='Código CPBS (8 caracteres)',
        help='Usado para dCodCPBScmp / dCodCPBSabr en XML DGI.',
    )
