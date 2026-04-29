# -*- coding: utf-8 -*-
"""
Carga de códigos DGI **Provincia–Distrito–Corregimiento** (P-D-C) desde ``hka_ubicaciones.csv``.

* Se ejecuta en el **post_init** al instalar el módulo.
* Tras **actualizar** el módulo a la versión que trae la migración ``post-reload_ubicaciones_dgi``,
  se vuelve a fusionar el catálogo (ver ``migrations/``).

``hka_ubicaciones.csv`` se genera a partir de la jerarquía tipo DGI (códigos de 6 dígitos
``cod_geo`` → P-D-C sin ceros a la izquierda por tramo), alineada al repositorio público
`listado-ubicaciones-panama` (M. Rios / molekilla). Compruebe actualizaciones ante la DGI.

Formato CSV: ``codigo,provincia,distrito,corregimiento`` — ``codigo`` = ``P-D-C`` (ej. ``8-10-7``).
"""
import csv
import logging
import os
import re

_logger = logging.getLogger(__name__)

CSV_FILENAME = 'hka_ubicaciones.csv'


def _normalize_codigo(codigo):
    """Devuelve código P-D-C normalizado (6 dígitos DGI → P-D-C)."""
    if not codigo:
        return ''
    raw = str(codigo).strip()
    return _codigo_a_pdc(raw) or raw


def _codigo_a_pdc(codigo):
    """Si el código es 6 dígitos (080834), devuelve P-D-C (8-8-34). Si ya es P-D-C, lo devuelve tal cual."""
    if not codigo:
        return ''
    s = str(codigo).strip()
    limpio = re.sub(r'\D', '', s)
    if len(limpio) == 6 and '-' not in s:
        return f"{int(limpio[0:2])}-{int(limpio[2:4])}-{int(limpio[4:6])}"
    return s


def _get_csv_path():
    """Ruta al CSV dentro del addon (junto a este script)."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_dir, CSV_FILENAME)


# Provincias de Panamá (códigos 01–10, DGI). Si ya existen no se agregan.
PANAMA_PROVINCIAS = (
    ('01', 'Bocas del Toro'),
    ('02', 'Chiriquí'),
    ('03', 'Coclé'),
    ('04', 'Colón'),
    ('05', 'Darién'),
    ('06', 'Herrera'),
    ('07', 'Los Santos'),
    ('08', 'Panamá'),
    ('09', 'Panamá Oeste'),
    ('10', 'Veraguas'),
)


def _ensure_panama_states(env):
    """
    Paso 1: Crea res.country.state (provincias PA) solo si no existen.
    Busca por country_id + name; si existe no agrega.
    """
    country = env['res.country'].with_context(active_test=False).search([('code', '=', 'PA')], limit=1)
    if not country:
        return
    State = env['res.country.state'].with_context(active_test=False)
    for code, name in PANAMA_PROVINCIAS:
        exists = State.search([
            ('country_id', '=', country.id),
            ('name', '=', name),
        ], limit=1)
        if not exists:
            State.create({
                'name': name,
                'country_id': country.id,
                'code': code,
            })
            _logger.info('FE_ETS: Creada provincia PA: %s (%s)', name, code)


def _ensure_panama_districts(env):
    """
    Paso 2: Distritos.
    En este módulo no hay modelo separado de distritos; cada distrito existe
    como valor del campo distrito en hka.codigo.ubicacion. Se cargan en el
    paso 4 (_load_hka_location_codes). Paso explícito para mantener la secuencia
    provincias → distritos → corregimientos → codigoUbicacion.
    """
    pass


def _ensure_panama_corregimientos(env):
    """
    Paso 3: Corregimientos.
    Igual que distritos: no hay modelo separado; se cargan en hka.codigo.ubicacion
    en el paso 4 (_load_hka_location_codes).
    """
    pass


def _limpiar_y_cargar_ubicaciones(env):
    """
    Una sola fuente (CSV): limpia la tabla, carga desde CSV y reasigna partners.
    Evita choque entre códigos 6 dígitos (XML) y P-D-C (CSV/HKA).
    """
    HkaUbicacion = env['hka.codigo.ubicacion'].sudo()
    Partner = env['res.partner'].sudo()
    # 1) Backup: partner_id -> (codigo, provincia, distrito, corregimiento)
    partners_con_ubicacion = Partner.search([('pa_codigo_ubicacion_id', '!=', False)])
    backup = []
    for p in partners_con_ubicacion:
        u = p.pa_codigo_ubicacion_id
        backup.append((p.id, u.codigo or '', u.provincia or '', u.distrito or '', u.corregimiento or ''))
    # 2) Quitar FK y borrar todos los códigos
    partners_con_ubicacion.write({'pa_codigo_ubicacion_id': False})
    HkaUbicacion.search([]).unlink()
    # 3) Cargar solo desde CSV (no XML)
    _load_from_csv(env)
    # 4) Reasignar: por código P-D-C o por provincia/distrito/corregimiento
    reasignados = 0
    for partner_id, codigo, provincia, distrito, corregimiento in backup:
        codigo_pdc = _codigo_a_pdc(codigo)
        hka = HkaUbicacion.search([('codigo', '=', codigo_pdc)], limit=1)
        if not hka and (provincia or distrito or corregimiento):
            domain = [('provincia', '=', provincia), ('distrito', '=', distrito), ('corregimiento', '=', corregimiento)]
            hka = HkaUbicacion.search(domain, limit=1)
        if hka:
            Partner.browse(partner_id).write({'pa_codigo_ubicacion_id': hka.id})
            reasignados += 1
    if backup:
        _logger.info('FE_ETS: Ubicaciones: tabla limpiada, cargada desde CSV; %s partners reasignados.', reasignados)
    return reasignados


def _load_hka_location_codes(env):
    """
    Paso 4: Fusiona filas desde ``hka_ubicaciones.csv`` (catálogo P-D-C) sin vaciar la tabla
    de forma destructiva: crea o actualiza por código P-D-C normalizado.
    """
    _load_from_csv(env)


def _load_from_csv(env):
    """
    Carga idempotente desde CSV.
    Actualiza res.country.state (provincias) y hka.codigo.ubicacion.
    """
    csv_path = _get_csv_path()
    if not os.path.isfile(csv_path):
        _logger.info('FE_ETS: No se encontró %s; omitiendo carga de ubicaciones desde CSV.', csv_path)
        return 0

    country = env['res.country'].with_context(active_test=False).search([('code', '=', 'PA')], limit=1)
    if not country:
        _logger.warning('FE_ETS: País PA no encontrado; no se cargan ubicaciones.')
        return 0

    State = env['res.country.state'].with_context(active_test=False)
    HkaUbicacion = env['hka.codigo.ubicacion'].sudo()
    created_states = set()
    created_hka = 0
    updated_hka = 0

    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        try:
            reader = csv.DictReader(f, fieldnames=('codigo', 'provincia', 'distrito', 'corregimiento'))
            for row in reader:
                codigo = _normalize_codigo(row.get('codigo', ''))
                if not codigo or codigo.lower() == 'codigo' or codigo.startswith('#'):
                    continue
                provincia = (row.get('provincia') or '').strip()
                distrito = (row.get('distrito') or '').strip()
                corregimiento = (row.get('corregimiento') or '').strip()
                if not provincia:
                    continue
                # Provincia -> res.country.state (idempotente)
                state_key = (country.id, provincia)
                if state_key not in created_states:
                    state = State.search([
                        ('country_id', '=', country.id),
                        ('name', '=', provincia),
                    ], limit=1)
                    if not state:
                        parts = re.split(r'[-\s]+', codigo)
                        code_prov = (parts[0] if parts else '8').zfill(2)
                        State.create({
                            'name': provincia,
                            'country_id': country.id,
                            'code': code_prov,
                        })
                        created_states.add(state_key)
                # hka.codigo.ubicacion (idempotente: crear o actualizar)
                hka = HkaUbicacion.search([('codigo', '=', codigo)], limit=1)
                vals = {
                    'provincia': provincia,
                    'distrito': distrito,
                    'corregimiento': corregimiento,
                }
                if hka:
                    hka.write(vals)
                    updated_hka += 1
                else:
                    HkaUbicacion.create({
                        'codigo': codigo,
                        'activo': True,
                        **vals,
                    })
                    created_hka += 1

        except Exception as e:
            _logger.exception('FE_ETS: Error leyendo CSV de ubicaciones: %s', e)
            return 0

    _logger.info(
        'FE_ETS: Ubicaciones CSV: %d creados hka.codigo.ubicacion, %d actualizados.',
        created_hka, updated_hka
    )
    return created_hka + updated_hka


def load_panama_locations(env):
    """
    Post-init hook: secuencia completa para facturación electrónica (solo en instalación).
    1. Provincias (res.country.state)
    2. Distritos (paso explícito; datos en hka.codigo.ubicacion)
    3. Corregimientos (paso explícito; datos en hka.codigo.ubicacion)
    4. Códigos HKA (CSV + XML, idempotente)
    """
    _ensure_panama_states(env)
    _ensure_panama_districts(env)
    _ensure_panama_corregimientos(env)
    _load_hka_location_codes(env)

    # Limpiar grupos duplicados (mantener el primero)
    # Odoo 19: res.groups tiene privilege_id; la categoría va en res.groups.privilege.category_id
    Category = env['ir.module.category']
    Privilege = env['res.groups.privilege']
    Group = env['res.groups']
    cat = Category.search(
        ['|', ('name', '=', 'Accounting'), ('name', '=', 'Contabilidad')],
        limit=1,
    )
    if cat:
        priv_ids = Privilege.search([('category_id', '=', cat.id)]).ids
        if priv_ids:
            groups = Group.search([
                ('privilege_id', 'in', priv_ids),
                ('name', 'ilike', 'Facturación Electrónica'),
            ], order='id')
            seen = {}
            to_delete = []
            for g in groups:
                key = (g.privilege_id.id, g.name)
                if key in seen:
                    to_delete.append(g.id)
                else:
                    seen[key] = g.id
            if to_delete:
                Group.browse(to_delete).unlink()
                _logger.info('FE_ETS: Eliminados %s grupos duplicados.', len(to_delete))
