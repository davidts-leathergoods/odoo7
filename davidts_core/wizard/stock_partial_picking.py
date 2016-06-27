# -*- coding: utf-8 -*-

from openerp.osv import osv

class stock_partial_picking(osv.osv_memory):

    _inherit = "stock.partial.picking"

    def _partial_move_for(self, cr, uid, move,context=None):
        partial_move = super(stock_partial_picking, self)._partial_move_for(cr, uid, move)
        if move.picking_id.type == 'out' or move.picking_id.type == 'in':
            partial_move.update({'quantity': move.wms_qty if move.state == 'assigned' else 0})
        return partial_move
