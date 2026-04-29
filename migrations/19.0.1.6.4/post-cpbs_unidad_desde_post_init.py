# -*- coding: utf-8 -*-
"""19.0.1.6.4: CPBS y unidad de medida pasan a cargarse en post_init (XML en disco, no en manifiesto data)."""
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
    mod.load_hka_data_catalogs_from_xml_files(env)
    _logger.info('FE_ETS: migración 19.0.1.6.4 — CPBS y unidad medida fusionados desde XML (idempotente).')
