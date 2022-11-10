from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PurchaseReport(models.TransientModel):
    _name = 'stock.picking.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    
    @api.multi
    def print_internal_transfer_report(self):
        transfers = self.env['stock.picking'].search(
            [ 
                '|', ('location_dest_id', 'ilike', 'MC2'),
                '|', ('location_dest_id', 'ilike', 'MC1'),
                '&', ('location_dest_id', 'ilike', 'TKJS/Stock'),
                '&', ('min_date', '<=', self.end_date),
                '&', ('min_date', '>=', self.start_date),
                '&', ('state', '=', 'done'),
                ('picking_type_id', 'ilike', 'Internal Transfers'),
            ], 
            order="min_date asc")

        transfer_data = []
        for transfer in transfers:
            temp = []
            transfer_detail = []
            for pack_operation in transfer.pack_operation_product_ids:
                detail = []
                detail.append(pack_operation.product_id.default_code) #kode
                detail.append(pack_operation.product_id.name) #nama
                detail.append(pack_operation.product_qty) #partner
                detail.append(pack_operation.product_uom_id.name) #satuan
                detail.append(pack_operation.product_qty) #jumlah
                transfer_detail.append(detail)
            
            temp.append(transfer.name)
            temp.append(transfer.min_date)
            temp.append(transfer.location_id.name)
            temp.append(transfer.location_dest_id.location_id.name)
            temp.append(transfer_detail)
            
            transfer_data.append(temp)
            
        datas = {
            'ids': self.ids,
            'model': 'purchase.order.report',
            'form': transfer_data,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'internal_transfer_report.internal_transfer_report_temp', data=datas)
