# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'ISO 20022 XML payment files',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'category': 'Generic Modules/Accounting',
    'description': """ 
    
ISO 20022 XML payment files
===========================

Module to generate Customer Credit Transfer Initiation message ISO 20022 XML - pain.001.001.03.

This module implements the following subset of the ISO 20022 specifications:

European Credit Transfers:
--------------------------
* debtor and creditor account in SEPA countries
* debtor account in Company currency
* creditor account in Company currency
* creditor account identified by BIC & IBAN
* support for single payments
        
The module also prohibits the removal of a confirmed Payment Order. 
Such a removal is still possible via the 'Undo Payment' button available to users of the 'Accounting / Manager' group.

Features targeted for the Belgian market (cf. febelfin guidelines):

* creditor account identified by IBAN (without BIC) for BE IBAN accounts
* support for belgian structured communication format
* by default, the right part of the VAT number (KBO/BCE number) is used to identify the Initiating Party

    """,
    'depends': ['account','base_iban', 'account_payment'],
    'demo_xml': [],
    'init_xml': [],
    'update_xml' : [
#        'security/ir.model.access.csv',
        'account_pain_wizard.xml',
        'account_payment_view.xml',      
    ],
    'active': False,
    'installable': True,
}
