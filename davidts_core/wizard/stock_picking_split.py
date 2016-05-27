# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare
from openerp.tools.translate import _

class StockPickingInSplitLine(osv.osv_memory):
    _name = "stock.picking.split.line"
    _inherit = "stock.partial.picking.line"
    _columns = {
        'wizard_id': fields.many2one('stock.picking.split', string="Wizard", ondelete='CASCADE'),
    }

class StockPickingInSplit(osv.osv_memory):
    _name = "stock.picking.split"
    _inherit = "stock.partial.picking"
    _columns = {
        'move_ids': fields.one2many('stock.picking.split.line', 'wizard_id', 'Product Moves'),
    }

    def do_split(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date': partial.date
        }
        picking_type = partial.picking_id.type
        for wizard_line in partial.move_ids:
            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id
            #Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

            #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

            if line_uom.factor and line_uom.factor != 0:
                if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'),
                                         _('The unit of measure rounding does not allow you to ship "%s %s", '
                                           'only rounding of "%s %s" is accepted by the Unit of Measure.')
                                         % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:
                #Check rounding Quantity.ex.
                #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                #partial delivery: 253g
                #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                #Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity/line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
                    raise osv.except_osv(_('Warning!'),
                                         _('The rounding of the initial uom does not allow you to ship "%s %s", as it '
                                           'would let a quantity of "%s %s" to ship and only rounding of "%s %s" is '
                                           'accepted by the uom.') % (wizard_line.quantity, line_uom.name,
                                                                      wizard_line.move_id.product_qty - without_rounding_qty,
                                                                      initial_uom.name, initial_uom.rounding,
                                                                      initial_uom.name))
            else:
                seq_obj_name = 'stock.picking.' + picking_type
                move_id = stock_move.create(cr, uid, {
                    'name': self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
                    'product_id': wizard_line.product_id.id,
                    'product_qty': wizard_line.quantity,
                    'product_uom': wizard_line.product_uom.id,
                    'prodlot_id': wizard_line.prodlot_id.id,
                    'location_id': wizard_line.location_id.id,
                    'location_dest_id': wizard_line.location_dest_id.id,
                    'picking_id': partial.picking_id.id
                }, context=context)
                #stock_move.action_confirm(cr, uid, [move_id], context)
            partial_data['move%s' % move_id] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.product_uom.id,
                'prodlot_id': wizard_line.prodlot_id.id,
            }
            if (picking_type=='in') and (wizard_line.product_id.cost_method=='average'):
                partial_data['move%s' % wizard_line.move_id.id].update(product_price=wizard_line.cost,
                                                                       product_currency=wizard_line.currency.id)
        self.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')

        for pick in picking_obj.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s' % move.id, {})
                product_qty = partial_data.get('product_qty', 0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', False)
                product_price = partial_data.get('product_price', 0.0)
                product_currency = partial_data.get('product_currency', False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty,
                                                            move.product_uom.id)

                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)
                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id not in product_avail:
                        # keep track of stock on hand including processed lines not yet marked as done
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                                         move_currency_id, product_price, round=False)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price, product.uom_id.id)
                        if product_avail[product.id] <= 0:
                            product_avail[product.id] = 0
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit*product_avail[product.id]) +
                                             (new_price*qty))/(product_avail[product.id]+qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id], {
                            'price_unit': product_price,
                            'price_currency_id': product_currency})

                        product_avail[product.id] += qty

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking_name = pick.name
                    picking_obj.write(cr, uid, [pick.id], {
                        'name': sequence_obj.get(cr, uid,
                        'stock.picking.%s' % pick.type),
                    })
                    new_picking = picking_obj.copy(cr, uid, pick.id, {
                        'name': new_picking_name,
                        'move_lines': [],
                        'state': 'draft',
                    })
                if product_qty != 0:
                    defaults = {
                        'product_qty': product_qty,
                        'product_uos_qty': product_qty,
                        'picking_id': new_picking,
                        'state': 'assigned',
                        'move_dest_id': False,
                        'price_unit': move.price_unit,
                        'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id], {
                    'product_qty': move.product_qty - partial_qty[move.id],
                    'product_uos_qty': move.product_qty - partial_qty[move.id],
                    'prodlot_id': False,
                    'tracking_id': False,
                })
            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty': product_qty,
                    'product_uos_qty': product_qty,
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                # Then we finish the good picking
                picking_obj.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                picking_obj.draft_force_assign(cr, uid, [new_picking], context)
                delivered_pack_id = pick.id
                back_order_name = picking_obj.browse(cr, uid, delivered_pack_id, context=context).name
                picking_obj.message_post(cr, uid, new_picking,
                                         body=_("Back order <em>%s</em> has been <b>created</b>.") % back_order_name,
                                         context=context)
            else:
                delivered_pack_id = pick.id

            delivered_pack = picking_obj.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
