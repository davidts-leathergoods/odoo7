# -*- coding: utf-8 -*-
##############################################################################
#
#    Audaxis, l'esprit libre
#    Copyright (C) 2014 Audaxis (<http://www.audaxis.com>).
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
    'name': 'ax_account_payment_order',
    'version': '0.1',   # Eg. 0.1 : Warning used for migration scripts
    'author': 'Audaxis',
    "category": 'Audaxis',
    'description': "Add balance on wizard for create payment order ",
    'complexity': 'middle',
    'website': '',
    'images': [],
    'depends': [
        'account_payment',
    ],
    'data': [
        "wizard/account_payment_create_order_view.xml",
    ],
    'demo': [
    ],
    'js': [],
    'qweb': [],
    'css': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
