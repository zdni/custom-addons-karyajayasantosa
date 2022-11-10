from openerp import api, fields, models, _

class purchase(models.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"

    @api.depends('amount_total')
    def _terbilang(self):
        for rec in self:
            amount = rec.amount_total
            terbilang = self.env['vit.terbilang'].terbilang(amount,'IDR')
            rec.terbilang = terbilang

    terbilang = fields.Char(string="Terbilang", required=False, compute="_terbilang")