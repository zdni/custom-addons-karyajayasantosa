from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class User(models.Model):
    _inherit = 'res.users'

    @api.multi
    def write(self, vals):
        old_pin = '|' + str( self.id ) + ':|'
        if self.pos_security_pin:
            old_pin = '|' + str( self.id ) + ':' + self.pos_security_pin + '|'
        
        new_pin = '|' + str( self.id ) + ':|'
        if vals.get('pos_security_pin'):
            new_pin = '|' + str( self.id ) + ':' + vals.get('pos_security_pin') + '|'
        
        where_like_pin = '%' + old_pin + '%'
        query = """
            SELECT id, string_pin
            FROM pos_config
            WHERE string_pin LIKE %s
        """
        params = [ where_like_pin ]
        self.env.cr.execute( query, params )
        pos_configs = self.env.cr.dictfetchall()

        for pos_config in pos_configs:
            pos_config = self.env['pos.config'].search([('id', '=', pos_config['id'])])
            replace_pin = pos_config['string_pin'].replace( old_pin, new_pin )
            pos_config.write({
                'string_pin': replace_pin,
            })
            
        result = super(User, self).write(vals)
        return result