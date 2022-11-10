{
	"name": "custom_report_internal", 
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
		"report/custom_agedpartnerledger.xml",
		"report/custom_financial.xml",
		"report/custom_generalledger.xml",
		"report/custom_header.xml",
		"report/custom_inventory.xml",
		"report/custom_journal.xml",
		"report/custom_partnerledger.xml",
		"report/custom_style.xml",
		"report/custom_trialbalance.xml",
	],
	"installable": True,
	"auto_install": False,
}