# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from lxml import etree

from openerp.osv import fields, osv
from openerp.tools.translate import _

class payment_order_create(osv.osv_memory):
    """
    Create a payment object with lines corresponding to the account move line
    to pay according to the date and the mode provided by the user.
    Hypothesis:
    - Small number of non-reconciled move line, payment mode and bank account type,
    - Big number of partner and bank account.

    If a type is given, unsuitable account Entry lines are ignored.
    """

    _inherit = 'payment.order.create'
    _columns = {
        'balance': fields.float('Balance', size=16, readonly="1"),
    }

    def onchange_entries(self, cr, uid, ids, entries, context=None):
        account_move_line_obj = self.pool.get('account.move.line')
        balance = 0.0
        if entries:
            for entrie in entries:
                move_id = entrie[2]
                if move_id:
                    move = account_move_line_obj.browse(cr, uid, move_id[0], context)
                    if move.invoice:
                        balance = move.invoice.residual
            return {'value': {'balance': balance}}
        return {'value': {'balance': balance}}

payment_order_create()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
