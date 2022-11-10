from openerp import api, fields, models, _

class invoice(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"

    @api.depends('amount_total')
    def _terbilang(self):
        for rec in self:
            amount = rec.amount_total
            terbilang = self.env['vit.terbilang'].terbilang(amount,'IDR')
            rec.terbilang = terbilang

    terbilang = fields.Char(string="Terbilang", required=False, compute="_terbilang")