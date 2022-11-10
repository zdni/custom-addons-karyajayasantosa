# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    lock_price = fields.Boolean(string="Otorisasi Perubahan Harga", default=False)
    lock_discount = fields.Boolean(string="Otorisasi Diskon", default=False)

    authorization_user_ids = fields.Many2many('res.users', string='Authorization User')
    string_pin = fields.Char(string='PIN')
    
    @api.constrains('authorization_user_ids')
    def check_pos_pin_authorization_user(self):
        string_pin = ''
        index = 0
        for user in self.authorization_user_ids:
            res_user = self.env['res.users'].search([('id', '=', user.id)])
            if not res_user.pos_security_pin:
                raise ValidationError(_("User " + res_user.name  + " Tidak Memiliki Security PIN"))
            if index == 0:
                string_pin = string_pin + '|' + str( res_user.id ) + ':' + res_user.pos_security_pin + '|'
            else:
                string_pin = string_pin + str( res_user.id ) + ':' + res_user.pos_security_pin + '|'
            index = index + 1
            
        self.write({'string_pin': string_pin})