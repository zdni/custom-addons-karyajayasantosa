from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ProfitPoSReport(models.TransientModel):
    _name = 'pos.report'

    start_date = fields.Date("Start Date", required=True) 
    end_date = fields.Date("End Date", required=True) 
    type_report = fields.Selection(
        [('detail', 'PoS Profit Detail'), ('summary','PoS Profit Rekap')], 
        string="Tipe Report",
        default='summary' 
    )

    @api.multi
    def print_profit_pos_report(self):
        sessions = self.env['pos.session'].search([ 
            ('stop_at', '<=', self.end_date),
            ('stop_at', '>=', self.start_date),
            ('state', '=', 'closed'),
        ], order="stop_at asc")
    
        session_data = []
        for session in sessions:
            temp = []
            temp_trans = []
            transactions = self.env['pos.order'].search([
                    ('session_id', '=', session.name),
                    ('state', '=', 'done'),
            ])

            total_hpp_transaction = 0
            for transaction in transactions:
                # check if retun transaction or not
                order = self.env['pos.order'].search([
                    ('pos_reference', '=', transaction.pos_reference)
                ], order="date_order asc, id asc", limit =1)
                is_return = True if transaction.id != order.id else False

                total_hpp_product = 0
                trans_data = []
                trans_line = []

                index = 0
                j = 0
                for line in transaction.lines:
                    if index < len(transaction.lines):
                        if not line.product_id.categ_id.is_consigment:
                            hpp_product = 0
                            if line.product_id.type == "product":
                                if is_return:
                                    find = False
                                    while not find:
                                        if j >= len(order.lines) or j >= len(order.picking_id.move_lines):
                                            break
                                        product_id = order.lines[j].product_id.id
                                        if product_id == line.product_id.id:
                                            find = True
                                            move_line = order.picking_id.move_lines[j]
                                            for quant_line in move_line.quant_ids:
                                                hpp_product += quant_line.inventory_value
                                            hpp_product = hpp_product*-1
                                        j += 1
                                else:
                                    find = False
                                    while not find:
                                        if index > len(transaction.picking_id.move_lines):
                                            break
                                        if transaction.picking_id.move_lines[index].product_id.id != line.product_id.id:
                                            index += 1
                                        else:
                                            find = True
                                            move_line = transaction.picking_id.move_lines[index]
                                            for quant_line in move_line.quant_ids:
                                                hpp_product += quant_line.inventory_value
                                
                                index += 1
                            lines = []
                            
                            if line.product_get_promo_id and line.product_get_promo_id.categ_id and line.product_get_promo_id.categ_id.is_consigment:
                                continue
                            if line.category_get_promo_id and line.category_get_promo_id.is_consigment:
                                continue
                            
                            uom = line.uom_id.name
                            qty = line.qty
                            
                            total_hpp_product += hpp_product

                            lines.append(line.product_id.name)
                            lines.append(uom)
                            lines.append(qty)
                            lines.append(line.discount)
                            lines.append(line.price_subtotal_incl)
                            lines.append(hpp_product)
                            trans_line.append(lines)

                amount_total = transaction.amount_total
                hpp_transaction = total_hpp_product
                margin_transaction = amount_total - total_hpp_product

                if len(trans_line) > 0:
                    if self.type_report == 'detail':
                        trans_data.append(transaction.pos_reference)
                        trans_data.append(trans_line)
                        trans_data.append(amount_total)
                        trans_data.append(hpp_transaction)
                        trans_data.append(margin_transaction)
                
                    temp_trans.append(trans_data)

                    total_hpp_transaction += hpp_transaction

            hpp_session = total_hpp_transaction

            temp.append(session.name) #0
            temp.append(session.user_id.name) #1
            temp.append(session.stop_at) #2session.statement_ids
            temp.append(hpp_session) #3
            temp.append(temp_trans) #4
            temp.append(self.type_report)
            
            total_trans = 0
            statements = {}
            for statement in session.statement_ids:
                statements[statement.journal_id.name] = statement.total_entry_encoding
                total_trans += statement.total_entry_encoding
            
            temp.append( statements )
            temp.append(total_trans)
            
            session_data.append(temp)

        datas = {
            'ids': self.ids,
            'model': 'pos.report',
            'form': session_data,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env['report'].get_action(self,'profit_pos_report.pos_report_temp', data=datas)
