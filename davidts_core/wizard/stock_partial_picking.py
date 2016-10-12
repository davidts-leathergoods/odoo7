# -*- coding: utf-8 -*-

from openerp.osv import osv

class stock_partial_picking(osv.osv_memory):

    _inherit = "stock.partial.picking"

    def _partial_move_for(self, cr, uid, move,context=None):
        partial_move = super(stock_partial_picking, self)._partial_move_for(cr, uid, move)
        if move.picking_id.type == 'out' or move.picking_id.type == 'in':
            partial_move.update({'quantity': move.wms_qty if move.state == 'assigned' else 0})
        return partial_move

    # latest version of Odoo7 opens the picking that has been done instead of keeping the remaining one
    # just closing is enought to satisfy davidts
    def do_partial(self, cr, uid, ids, context=None):
        super(stock_partial_picking,self).do_partial(cr,uid,ids,context=None)
        return {'type': 'ir.actions.act_window_close'}
