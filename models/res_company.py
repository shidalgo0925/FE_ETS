# -*- coding: utf-8 -*-
import hashlib
from datetime import timedelta

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    hka_integration_mode = fields.Selection(
        [
            ('direct_hka', 'Directo HKA (actual)'),
            ('ets_api', 'API ETS externa (opción 2)'),
        ],
        string='Modo de integración FE',
        default='direct_hka',
        required=True,
    )
    hka_backend_url = fields.Char(
        string='URL API ETS',
        help='Base URL del backend ETS, por ejemplo: https://api.midominio.com',
    )
    hka_backend_token = fields.Char(
        string='Token API ETS',
        help='Token Bearer opcional para autenticar contra la API ETS.',
    )
    hka_backend_timeout = fields.Integer(
        string='Timeout API ETS (s)',
        default=30,
    )
    hka_license_key = fields.Char(string='Codigo de licencia FE_ETS')
    hka_license_status = fields.Selection(
        [
            ('active', 'Activa'),
            ('grace', 'Gracia'),
            ('expired', 'Vencida'),
            ('suspended', 'Suspendida'),
            ('invalid', 'Invalida'),
            ('unknown', 'Sin validar'),
        ],
        string='Estado licencia',
        default='unknown',
        readonly=True,
    )
    hka_license_expires_at = fields.Datetime(string='Licencia expira', readonly=True)
    hka_license_last_check = fields.Datetime(string='Ultima validacion licencia', readonly=True)
    hka_license_grace_until = fields.Datetime(string='Gracia hasta', readonly=True)
    hka_license_grace_hours = fields.Integer(string='Horas de gracia', readonly=True, default=72)
    hka_license_message = fields.Char(string='Mensaje licencia', readonly=True)
    hka_license_server_url = fields.Char(
        string='URL servidor licencias',
        default='http://127.0.0.1:8899',
        help='Base URL para validar licencias (ej: https://licencias.ets.com).',
    )
    hka_license_server_token = fields.Char(
        string='Token servidor licencias',
        help='Token Bearer para endpoint /api/v1/license/validate.',
    )
    hka_usuario = fields.Char(string='Usuario del servicio (PAC)')
    hka_clave = fields.Char(string='Contraseña del servicio')
    hka_ambiente = fields.Selection(
        [('demo', 'Demo / Pruebas'), ('production', 'Producción')],
        string='Ambiente',
        default='demo',
    )
    hka_ruc = fields.Char(string='RUC emisor (DGI)')
    hka_dv = fields.Char(string='DV (emisor)')
    hka_punto_facturacion = fields.Char(string='Punto de facturación', default='001')
    hka_codigo_sucursal = fields.Char(string='Código sucursal', default='0000')
    hka_tipo_sucursal = fields.Selection(
        [
            ('1', 'Principal'),
            ('2', 'Secundaria'),
        ],
        string='Tipo sucursal',
        default='1',
    )
    hka_formato_cafe = fields.Selection(
        [
            ('1', 'Sin generación de CAFE'),
            ('2', 'Imagen'),
            ('3', 'Papel formato carta'),
        ],
        string='Formato CAFE',
        default='2',
    )
    hka_entrega_cafe = fields.Selection(
        [
            ('1', 'Sin generación de CAFE'),
            ('2', 'CAFE en papel al receptor'),
            ('3', 'Email'),
        ],
        string='Entrega CAFE',
        default='3',
    )
    hka_auto_send = fields.Boolean(
        string='Enviar automáticamente al confirmar factura',
        default=False,
    )
    hka_numero_licencia = fields.Char(string='Número de licencia')
    hka_folios_disponibles = fields.Integer(
        string='Folios disponibles',
        default=0,
    )
    hka_ultima_sincronizacion = fields.Datetime(string='Última sincronización')

    def action_hka_test_connection(self):
        """Prueba usuario/clave contra la API de autenticación HKA."""
        self.ensure_one()
        if not self.hka_usuario or not self.hka_clave:
            raise UserError(_('Indique usuario y contraseña del servicio de facturación.'))
        client = self._get_hka_client()
        res = client.authenticate()
        if res.get('success'):
            self.sudo().write({
                'hka_ultima_sincronizacion': fields.Datetime.now(),
            })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Conexión al servicio'),
                    'message': _('Conexión correcta (%s, ambiente %s).') % (
                        'API ETS' if self.hka_integration_mode == 'ets_api' else 'HKA directo',
                        (self.hka_ambiente or 'demo'),
                    ),
                    'type': 'success',
                    'sticky': False,
                },
            }
        raise UserError(_('No se pudo conectar con el servicio de facturación: %s') % (res.get('error') or _('Error desconocido')))

    def _get_hka_client(self):
        self.ensure_one()
        from .hka_api import HKAApiClient, ETSBridgeApiClient

        if self.hka_integration_mode == 'ets_api':
            if not self.hka_backend_url:
                raise UserError(_('Configure la URL API ETS en la empresa para usar el modo API ETS externa.'))
            return ETSBridgeApiClient(
                self.hka_usuario,
                self.hka_clave,
                self.hka_ambiente or 'demo',
                backend_url=self.hka_backend_url,
                backend_token=self.hka_backend_token,
                timeout=self.hka_backend_timeout or 30,
            )
        return HKAApiClient(
            self.hka_usuario,
            self.hka_clave,
            self.hka_ambiente or 'demo',
        )

    def _license_payload(self):
        self.ensure_one()
        ICP = self.env['ir.config_parameter'].sudo()
        db_uuid = ICP.get_param('database.uuid') or self.env.cr.dbname
        base_url = (ICP.get_param('web.base.url') or 'http://localhost').strip()
        company_vat = (self.hka_ruc or self.vat or 'NA').strip()
        raw = f"{db_uuid}|{base_url}|{company_vat}"
        fingerprint = hashlib.sha256(raw.encode('utf-8')).hexdigest()
        return {
            'license_key': (self.hka_license_key or '').strip(),
            'db_uuid': db_uuid,
            'base_url': base_url,
            'module_name': 'FE_ETS',
            'module_version': self.env['ir.module.module'].search([('name', '=', 'FE_ETS')], limit=1).latest_version or '',
            'company_vat': company_vat,
            'instance_fingerprint': fingerprint,
        }

    def _call_license_validate(self):
        self.ensure_one()
        if not self.hka_license_server_url:
            raise UserError(_('Configure la URL del servidor de licencias.'))
        if not self.hka_license_key:
            raise UserError(_('Ingrese el codigo de licencia FE_ETS.'))
        payload = self._license_payload()
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.hka_license_server_token:
            headers['Authorization'] = f'Bearer {self.hka_license_server_token}'
        url = f"{self.hka_license_server_url.rstrip('/')}/api/v1/license/validate"
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            data = res.json()
        except requests.exceptions.RequestException as e:
            raise UserError(_('No se pudo conectar al servidor de licencias: %s') % str(e)) from e
        except Exception as e:
            raise UserError(_('Respuesta invalida del servidor de licencias: %s') % str(e)) from e

        status = data.get('status') or ('active' if data.get('valid') else 'invalid')
        grace_hours = int(data.get('grace_hours') or self.hka_license_grace_hours or 72)
        vals = {
            'hka_license_status': status if status in {'active', 'grace', 'expired', 'suspended', 'invalid', 'unknown'} else 'invalid',
            'hka_license_message': data.get('message') or '',
            'hka_license_last_check': fields.Datetime.now(),
            'hka_license_grace_hours': grace_hours,
        }
        exp = data.get('expires_at')
        if exp:
            try:
                vals['hka_license_expires_at'] = fields.Datetime.to_datetime(exp.replace('Z', '+00:00'))
            except Exception:
                vals['hka_license_expires_at'] = False
        else:
            vals['hka_license_expires_at'] = False
        if status == 'grace':
            vals['hka_license_grace_until'] = fields.Datetime.now() + timedelta(hours=grace_hours)
        elif status == 'active':
            vals['hka_license_grace_until'] = False
        self.sudo().write(vals)
        return data

    def _license_status_message(self, status):
        return {
            'expired': _('Licencia vencida. Contacte a soporte ETS para renovacion.'),
            'suspended': _('Licencia suspendida. Contacte a soporte ETS.'),
            'invalid': _('Licencia invalida. Revise el codigo e intente nuevamente.'),
            'unknown': _('Licencia sin validar. Active o revalide la licencia FE_ETS.'),
        }.get(status, _('Licencia no valida para esta operacion.'))

    def _is_license_check_stale(self, max_age_hours=12):
        self.ensure_one()
        if not self.hka_license_last_check:
            return True
        last = fields.Datetime.to_datetime(self.hka_license_last_check)
        return (fields.Datetime.now() - last) > timedelta(hours=max_age_hours)

    def _activate_grace_mode_if_possible(self, reason_message=''):
        self.ensure_one()
        if self.hka_license_status not in ('active', 'grace'):
            return False
        if not self.hka_license_last_check:
            return False
        grace_hours = int(self.hka_license_grace_hours or 72)
        last = fields.Datetime.to_datetime(self.hka_license_last_check)
        grace_until = last + timedelta(hours=grace_hours)
        now = fields.Datetime.now()
        if now > grace_until:
            return False
        msg = _('Sin conexion. Operando en modo gracia (%s h).') % grace_hours
        if reason_message:
            msg = f"{msg} {reason_message}"
        self.sudo().write({
            'hka_license_status': 'grace',
            'hka_license_grace_until': grace_until,
            'hka_license_message': msg,
        })
        return True

    def ensure_hka_license_allows_operation(self, operation_name='operación FE'):
        self.ensure_one()
        if not self.hka_license_key:
            raise UserError(_('No hay codigo de licencia FE_ETS configurado para %s.') % operation_name)

        status = self.hka_license_status or 'unknown'
        requires_refresh = self._is_license_check_stale() or status in ('unknown', 'invalid')
        if requires_refresh:
            try:
                self._call_license_validate()
                status = self.hka_license_status or 'unknown'
            except UserError as e:
                if self._activate_grace_mode_if_possible(str(e)):
                    return True
                raise UserError(_('No se pudo validar la licencia y no hay gracia disponible: %s') % str(e)) from e

        if status in ('active', 'grace'):
            if self.hka_license_expires_at:
                expires = fields.Datetime.to_datetime(self.hka_license_expires_at)
                if fields.Datetime.now() > expires and status != 'grace':
                    self.sudo().write({'hka_license_status': 'expired'})
                    raise UserError(self._license_status_message('expired'))
            return True

        raise UserError(self._license_status_message(status))

    def action_hka_activate_license(self):
        self.ensure_one()
        data = self._call_license_validate()
        ok = bool(data.get('valid'))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Licenciamiento FE_ETS'),
                'message': data.get('message') or (_('Licencia validada correctamente.') if ok else _('Licencia no valida.')),
                'type': 'success' if ok else 'warning',
                'sticky': not ok,
            },
        }

    def action_hka_revalidate_license(self):
        self.ensure_one()
        return self.action_hka_activate_license()
