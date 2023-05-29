# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    lock_order = fields.Boolean(string="Otorisasi Penjualan dibawah Stok", default=False)

    authorization_order_user_ids = fields.Many2many('res.users', string='Authorization User')
    string_pin_order = fields.Char(string='PIN')
    
    @api.constrains('authorization_order_user_ids')
    def check_pos_pin_authorization_user(self):
        string_pin_order = ''
        index = 0
        for user in self.authorization_order_user_ids:
            res_user = self.env['res.users'].search([('id', '=', user.id)])
            if not res_user.pos_security_pin:
                raise ValidationError(_("User " + res_user.name  + " Tidak Memiliki Security PIN"))
            if index == 0:
                string_pin_order = string_pin_order + '|' + str( res_user.id ) + ':' + res_user.pos_security_pin + '|'
            else:
                string_pin_order = string_pin_order + str( res_user.id ) + ':' + res_user.pos_security_pin + '|'
            index = index + 1
            
        self.write({'string_pin_order': string_pin_order})