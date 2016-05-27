# =============================================================================
#                                                                             =
#    ax_check_letter module for Odoo
#    Copyright (C) 2015 Audaxis (<http://www.audaxis.com>)
#                                                                             =
#    ax_check_letter is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License v3 or later
#    as published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#                                                                             =
#    ax_check_letter is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License v3 or later for more details.
#                                                                             =
#    You should have received a copy of the GNU Affero General Public License
#    v3 or later along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#                                                                             =
# =============================================================================
{
    'name': 'ax check letter',
    'version': '0.1',
    'description': """
    Can edit check letter (in french "lettre chèque")
    """,
    'summary': "",
    'icon': '/ax_check_letter/static/description/icon.png',
    'author': 'SAn, CMo',
    'website': 'http://www.audaxis.com',
    'license': 'AGPL-3',
    'category': 'accounting',
    'depends': ['account_voucher'],
    'data': [
        'security/ir.model.access.csv',
        'view/account_invoice.xml',
        'report/check_letter.xml',

        'wizards/pay_check_letter_unit.xml',

        'view/account_voucher.xml',

        'wizards/pay_check_letter_batch.xml',
        'wizards/print_check_letter.xml',
        'data/ir_sequence.xml',
        'data/check_letter.xml',
    ],
    'demo': [
    ],
    'auto_install': False,
    'web': False,
    'post_load': None,
    'application': False,
    'installable': True,
    'sequence': 150,
}
