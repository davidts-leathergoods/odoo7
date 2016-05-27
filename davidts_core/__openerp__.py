#  -*- coding: utf-8 -*-

# dependance supprimée ...
# "base_custom_attributes", "product_custom_attributes"

{
    "name": "Davidts",
    "version": "0.1",
    "author": "Audaxis",
    "category": 'Audaxis',
    'complexity': "easy",
    "description": """
        Davidts V1
    """,
    'website': 'http://www.openerp.com',
    'images': [],
    'init_xml': [],
    "depends": ["base", "crm", "sale", "product_template_links", "stock", "purchase", "account_voucher", "product_variant_multi", "product_variant_multi_advanced", "analytic",
            "l10n_be_coda", "account_pain", "account_followup_choose_partners", 
            "l10n_be_invoice_bba", "delivery", "sale_order_dates", "jasper_server", "sale_stock", "document", "crm_claim","project", "davidts_ext","report_webkit","account_financial_report_webkit",
            ],
    'data': [
         "views/account_bank_statement.xml",

        "wizard/stock_picking_split_view.xml",
        "views/partner.xml",
        "views/characteristic.xml",
        "views/product_template.xml",
        "views/product.xml",
        "views/product_variant.xml",
        "views/sale.xml",
        "views/discount_account_invoice.xml",
        "views/stock_picking.xml",
        "views/account_invoice.xml",
        "views/sale_config.xml",
        "views/type_event.xml",
        "views/event.xml",
        "views/purchase_view.xml",
        "views/charte_view.xml",
        "views/planificateur_talend.xml",
        "views/stock_expedition.xml",
        "views/crm_claim.xml",
        "views/users_view.xml",
        "views/account_move_view.xml",

        "wizard/stock_prevu_view.xml",
        "wizard/sol_mv_detail_view.xml",
        "wizard/schedulers_all_view.xml",
        "wizard/account_report_aged_partner_balance_view.xml",
        "data/ir_sequence.xml",
        "data/sale_process.xml",
        "data/sale_template.xml",
    ],
    'demo_xml': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
#  vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
