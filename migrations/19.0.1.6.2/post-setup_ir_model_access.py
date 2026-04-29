# -*- coding: utf-8 -*-
"""19.0.1.6.2: permisos movidos de CSV a Python; asegurar ir.model.access en DB existentes."""
import importlib
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    mod = None
    for name in ('odoo.addons.fe_ets', 'odoo.addons.FE_ETS'):
        try:
            mod = importlib.import_module(f'{name}.data.load_panama_locations')
            break
        except ImportError:
            continue
    if not mod:
        return
    mod.setup_ir_model_access(env)
    _logger.info('FE_ETS: migración 19.0.1.6.2 — permisos ir.model.access asegurados (código).')
