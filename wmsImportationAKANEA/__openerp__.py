# -*- coding: utf-8 -*-

{
    'name': 'ImportFromAKANEA',
    'version': '0.32.9',
    'author': 'Alain LEGRAND',
    'depends': ['base','base_setup','resource','stock','product','sale'],
    'data': [
             'wizard/scheduler_wms_akanea.xml',
             'wms_akanea_internal_mvt_view.xml',
             'wizard/multi_import_stock_mvt_wizard.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
    'application': False,
    'auto_install': False,
}