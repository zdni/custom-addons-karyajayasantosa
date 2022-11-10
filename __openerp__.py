{
	"name": "custom_report", 
	"version": "1.0", 
	"depends": [
		"base",
		"report",
		"sale",
		"purchase",
		"account",
		"stock",
	], 
	"author": "alzidni2000@gmail.com", 
	"category": "report", 
	"description": """\
Custom report for: \n
1. Purchase Order \n
2. Vendor Bills \n
3. Sales Order \n
4. Invoices \n
5. Delivery Order \n
6. Delivery Slip \n\n

with background, signature, and be calculated
""",
	"data": [
		"report/background_report.xml",
		"report/custom_barcode.xml",
		"report/custom_header.xml",
		"report/custom_picking.xml",
		"report/custom_report_external_layout.xml",
		"report/custom_style.xml",
		"report/delivery_slip.xml",
		"report/invoice.xml",
		"report/purchase_order.xml",
		"report/rfq.xml",
		"report/saleorder.xml",
	],
	"installable": True,
	"auto_install": False,
}