# -*- coding: utf-8 -*-
import importlib
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Vuelve a cargar el catálogo P-D-C desde hka_ubicaciones.csv (p. ej. al ampliar el CSV)."""
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    mod = None
    for name in ('odoo.addons.fe_ets', 'odoo.addons.FE_ETS'):
        try:
            mod = importlib.import_module(f'{name}.data.load_panama_locations')
            break
        except ImportError:
            continue
    if mod is None:
        _logger.error('FE_ETS: no se pudo importar load_panama_locations para migración de ubicaciones.')
        return
    mod.load_panama_locations(env)
    _logger.info('FE_ETS: migración 19.0.1.6.0 — catálogo de ubicaciones DGI recargado desde CSV.')
