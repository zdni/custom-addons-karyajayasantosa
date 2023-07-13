from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class ResUser(models.Model):
    _inherit = 'res.users'

    @api.multi
    def write(self, vals):
        for record in self:
            old_pin = '|' + str( record.id ) + ':|'
            if record.pos_security_pin:
                old_pin = '|' + str( record.id ) + ':' + record.pos_security_pin + '|'
            
            new_pin = '|' + str( record.id ) + ':|'
            if vals.get('pos_security_pin'):
                new_pin = '|' + str( record.id ) + ':' + vals.get('pos_security_pin') + '|'
            
            where_like_pin = '%' + old_pin + '%'
            query = """
                SELECT id, string_pin_order
                FROM pos_config
                WHERE string_pin_order LIKE %s
            """
            params = [ where_like_pin ]
            self.env.cr.execute( query, params )
            pos_configs = self.env.cr.dictfetchall()

            for pos_config in pos_configs:
                pos_config = self.env['pos.config'].search([('id', '=', pos_config['id'])])
                replace_pin = pos_config['string_pin_order'].replace( old_pin, new_pin )
                pos_config.write({
                    'string_pin_order': replace_pin,
                })
                
        return super(ResUser, self).write(vals)