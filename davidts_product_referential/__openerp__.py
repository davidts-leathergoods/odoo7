#  -*- coding: utf-8 -*-

{
"name": "Davidts Products Referencial",
"version": "0.1",
"author": "BPSO",
"sequence": 1,
"category": 'bpso',
'complexity': "easy",
"description": """
Davidts Products Referencial
============================
* Add new referential attributes on products
* Add Companies
    
""",
'website': 'http://www.bpso.biz',
'images': [],
'init_xml': [],
"depends": ["base","product","web","davidts_core"],
'data': [
         "security/davidts_security.xml",
         "views/product_view.xml",
         "views/davidts_metier.xml",
         "security/ir.model.access.csv",
         "data/product_referential_data.xml",
         "data/product_companies_data.xml",
        ],
'demo_xml': [
],
'test': [
],
'installable': True,
'auto_install': False,
}
#  vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: