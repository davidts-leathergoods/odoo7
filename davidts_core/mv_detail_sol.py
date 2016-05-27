from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import datetime

class sol_mv_details(osv.osv):
    _name = 'sol.mv.details'
    _description = 'class of mv_details'

    def get_product_available2(self, cr, uid, ids, context=None):
        """ Finds whether product is available or not in particular warehouse.
        @return: Dictionary of values
        """
        
        if context is None:
            context = {}
        location_obj = self.pool.get('stock.location')
        warehouse_obj = self.pool.get('stock.warehouse')
        shop_obj = self.pool.get('sale.shop')
        states = context.get('states', [])
        what = context.get('what', ())
        if not ids:
            ids = self.search(cr, uid, [])
        res = {}.fromkeys(ids, 0.0)
        if not ids:
            return res
        if context.get('shop', False):
            warehouse_id = shop_obj.read(cr, uid, int(context['shop']), ['warehouse_id'])['warehouse_id'][0]
            if warehouse_id:
                context['warehouse'] = warehouse_id
        if context.get('warehouse', False):
            lot_id = warehouse_obj.read(cr, uid, int(context['warehouse']), ['lot_stock_id'])['lot_stock_id'][0]
            if lot_id:
                context['location'] = lot_id
        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = location_obj.search(cr, uid, [('name', 'ilike', context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = []
            wids = warehouse_obj.search(cr, uid, [], context=context)
            if not wids:
                return res
            for w in warehouse_obj.browse(cr, uid, wids, context=context):
                location_ids.append(w.lot_stock_id.id)
        if context.get('compute_child', True):
            child_location_ids = location_obj.search(cr, uid, [('location_id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids
        product2uom = {}
        uom_ids = []
        for product in self.pool.get('product.product').read(cr, uid, ids, ['uom_id'], context=context):
            product2uom[product['id']] = product['uom_id'][0]
            uom_ids.append(product['uom_id'][0])
        uoms_o = {}
        for uom in self.pool.get('product.uom').browse(cr, uid, uom_ids, context=context):
            uoms_o[uom.id] = uom
        results = []
        results2 = []
        from_date = context.get('from_date', False)
        to_date = context.get('to_date', False)
        date_str = False
        date_values = False
        where = [tuple(location_ids), tuple(location_ids), tuple(ids), tuple(states)]
        if from_date and to_date:
            date_str = "st.date_expected>=%s and st.date_expected<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "st.date_expected>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "st.date_expected<=%s"
            date_values = [to_date]
        if date_values:
            where.append(tuple(date_values))
        prodlot_id = context.get('prodlot_id', False)
        prodlot_clause = ''
        if prodlot_id:
            prodlot_clause = ' and st.prodlot_id = %s '
            where += [prodlot_id]
        if 'in' in what:
            cr.execute(
                'select sum(st.product_qty), st.product_id, st.product_uom '\
                'from stock_move st '\
                'where st.location_id NOT IN %s '\
                'and st.location_dest_id IN %s '\
                'and st.product_id IN %s '\
                'and st.state IN %s ' + (date_str and 'and ' + date_str + ' ' or '') + ' '\
                + prodlot_clause +
                'group by st.product_id,st.product_uom', tuple(where))
            results = cr.fetchall()
        if 'out' in what:
            cr.execute(
                'select sum(st.product_qty), st.product_id, st.product_uom '\
                'from stock_move st '\
                'where st.location_id IN %s '\
                'and st.location_dest_id NOT IN %s '\
                'and st.product_id  IN %s '\
                'and st.state in %s ' + (date_str and 'and ' + date_str + ' ' or '') + ' '\
                + prodlot_clause +
                ' group by st.product_id,st.product_uom ', tuple(where))
            results2 = cr.fetchall()
        uom_obj = self.pool.get('product.uom')
        uoms = map(lambda x: x[2], results) + map(lambda x: x[2], results2)
        if context.get('uom', False):
            uoms += [context['uom']]
        uoms = filter(lambda x: x not in uoms_o.keys(), uoms)
        if uoms:
            uoms = uom_obj.browse(cr, uid, list(set(uoms)), context=context)
            for o in uoms:
                uoms_o[o.id] = o
        context.update({'raise-exception': False})
        for amount, prod_id, prod_uom in results:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                     uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] += amount
        for amount, prod_id, prod_uom in results2:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                    uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] -= (amount)
        return res

    def _product_available2(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """

        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        for f in field_names:
            c = context.copy()
            for id in ids:
                mv_detail = self.browse(cr, uid, id)
                rang = mv_detail.mumero_semain
                if f == 'qty_available_week_fn':
                    prod = self.browse(cr, uid, id).product_id.id
                    if rang == 0:
                        dt_to = datetime.datetime.now() + datetime.timedelta(days=(7*rang))
                        str_dt_to = str(dt_to)[0:10]
                        dt_from = datetime.datetime.now() + datetime.timedelta(days=7*(rang-1) + 1)
                        str_dt_from = str(dt_from)[0:10]
                        c.update({'states': ('done',), 'what': ('in', 'out')})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        prod = self.browse(cr, uid, id).product_id.id
                        res[id][f] = stock.get(prod, 0.0)
                    if rang <> 0:
                        dt_to = datetime.datetime.now() + datetime.timedelta(days=(7*(rang-1)))
                        str_dt_to = str(dt_to)[0:10]
                        c.update({'states': ('done',), 'what': ('in', 'out'), 'to_date': ''})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        virtual_available = stock.get(prod, 0.0)
                        c.update({'states': ('confirmed', 'waiting', 'assigned'), 'what': ('in', 'out'), 'to_date': str_dt_to})
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        virtual_available = virtual_available + stock.get(prod, 0.0)
                        res[id][f] = virtual_available
                    where = []
                    where = [tuple([mv_detail.product_id.id])]
                    cr.execute('SELECT mumero_semain,sol_product_qty FROM sol_mv_details where product_id = %s and sol_product_qty <> 0;', tuple(where))
                    results3 = cr.fetchall()
                    x = results3[0]
                    if rang > x[0] and rang != 0:
                        res[id][f] -= x[1]
                if f == 'virtual_available_week_fn':
                    if rang < 10:
                        prod = self.browse(cr, uid, id).product_id.id
                        virtual_available = 0.0
                        dt_to = datetime.datetime.now() + datetime.timedelta(days=(7*rang))
                        str_dt_to = str(dt_to)[0:10]
                        dt_from = datetime.datetime.now() + datetime.timedelta(days=7*(rang-1) + 1)
                        str_dt_from = str(dt_from)[0:10]
                        c.update({'states': ('done',), 'what': ('in', 'out'), 'to_date': ''})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        virtual_available = stock.get(prod, 0.0)
                        c.update({'states': ('confirmed', 'waiting', 'assigned'), 'what': ('in', 'out'), 'to_date': str_dt_to})
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        virtual_available = virtual_available + stock.get(prod, 0.0)
                        res[id][f] = virtual_available
                    if rang == 10:
                        prod = self.browse(cr, uid, id).product_id.id
                        virtual_available = 0.0
                        dt_to = datetime.datetime.now() + datetime.timedelta(days=7*rang)
                        str_dt_to = str(dt_to)[0:10]
                        dt_from = datetime.datetime.now() + datetime.timedelta(days=7*(rang-1) + 1)
                        str_dt_from = str(dt_from)[0:10]
                        c.update({'states': ('done',), 'what': ('in', 'out'), 'to_date': ''})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        virtual_available = stock.get(prod, 0.0)
                        c.update({'states': ('confirmed', 'waiting', 'assigned'), 'what': ('in', 'out'), 'to_date': ''})
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        virtual_available = virtual_available + stock.get(prod, 0.0)
                        res[id][f] = virtual_available
                    where = []
                    where = [tuple([mv_detail.product_id.id])]
                    cr.execute('SELECT mumero_semain,sol_product_qty FROM sol_mv_details where product_id = %s and sol_product_qty <> 0;', tuple(where))
                    results4 = cr.fetchall()
                    x = results4[0]
                    if rang >= x[0]:
                        res[id][f] -= x[1]

                if f == 'incoming_qty_week_fn':
                    if rang == 0:
                        prod = self.browse(cr, uid, id).product_id.id
                        dt_to = datetime.datetime.now()
                        str_dt_to = str(dt_to)[0:10]
                        dt_from = datetime.datetime.now()
                        str_dt_from = str(dt_from)[0:10]
                        c.update({'states': ('confirmed', 'waiting', 'assigned'), 'what': ('in',), 'from_date': str_dt_from, 'to_date': str_dt_to})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        prod = self.browse(cr, uid, id).product_id.id
                        res[id][f] = stock.get(prod, 0.0)
                    elif rang < 10:
                        prod = self.browse(cr, uid, id).product_id.id
                        dt_to = datetime.datetime.now() + datetime.timedelta(days=(7*rang))
                        str_dt_to = str(dt_to)[0:10]
                        dt_from = datetime.datetime.now() + datetime.timedelta(days=7*(rang-1) + 1)
                        str_dt_from = str(dt_from)[0:10]
                        c.update({'states': ('confirmed', 'waiting', 'assigned'), 'what': ('in',), 'from_date': str_dt_from, 'to_date': str_dt_to})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        prod = self.browse(cr, uid, id).product_id.id
                        res[id][f] = stock.get(prod, 0.0)
                    elif rang == 10:
                        prod = self.browse(cr, uid, id).product_id.id
                        dt_to = datetime.datetime.now() + datetime.timedelta(days=(7*rang))
                        str_dt_to = str(dt_to)[0:10]
                        dt_from = datetime.datetime.now() + datetime.timedelta(days=7*(rang-1) + 1)
                        str_dt_from = str(dt_from)[0:10]
                        c.update({'states': ('confirmed', 'waiting', 'assigned'), 'what': ('in',), 'from_date': str_dt_from, 'to_date': ''})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        prod = self.browse(cr, uid, id).product_id.id
                        res[id][f] = stock.get(prod, 0.0)

                if f == 'outgoing_qty_week_fn':
                    if rang == 0:
                        prod = self.browse(cr, uid, id).product_id.id
                        dt_to = datetime.datetime.now()
                        str_dt_to = str(dt_to)[0:10]
                        dt_from = datetime.datetime.now()
                        str_dt_from = str(dt_from)[0:10]
                        c.update({'states': ('confirmed', 'waiting', 'assigned'), 'what': ('out',), 'from_date': str_dt_from, 'to_date': str_dt_to})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        prod = self.browse(cr, uid, id).product_id.id
                        res[id][f] = stock.get(prod, 0.0)
                    elif rang < 10:
                        prod = self.browse(cr, uid, id).product_id.id
                        dt_to = datetime.datetime.now() + datetime.timedelta(days=(7*rang))
                        str_dt_to = str(dt_to)[0:10]
                        dt_from = datetime.datetime.now() + datetime.timedelta(days=7*(rang-1) + 1)
                        str_dt_from = str(dt_from)[0:10]
                        c.update({'states': ('confirmed', 'waiting', 'assigned'), 'what': ('out',), 'from_date': str_dt_from, 'to_date': str_dt_to})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        prod = self.browse(cr, uid, id).product_id.id
                        res[id][f] = stock.get(prod, 0.0)
                    elif rang == 10:
                        prod = self.browse(cr, uid, id).product_id.id
                        dt_to = datetime.datetime.now() + datetime.timedelta(days=(7*rang))
                        str_dt_to = str(dt_to)[0:10]
                        dt_from = datetime.datetime.now() + datetime.timedelta(days=7*(rang-1) + 1)
                        str_dt_from = str(dt_from)[0:10]
                        c.update({'states': ('confirmed', 'waiting', 'assigned'), 'what': ('out',), 'from_date': str_dt_from, 'to_date': ''})
                        product = self.browse(cr, uid, ids[0]).product_id.id
                        list_product = []
                        list_product.append(product)
                        stock = self.get_product_available2(cr, uid, list_product, context=c)
                        prod = self.browse(cr, uid, id).product_id.id
                        res[id][f] = stock.get(prod, 0.0)
                    res[id][f] -= mv_detail.sol_product_qty
        return res

    def _date_debut_fn(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for mv_details in self.browse(cr, uid, ids, context=context):
            rang = mv_details.mumero_semain
            if rang == 0:
                msg = _('this moment')
                res[mv_details.id] = msg
            else:
                dt_from = datetime.datetime.now() + datetime.timedelta(days=7*(rang-1) + 1)
                str_dt_from = str(dt_from)[0:10]
                res[mv_details.id] = str_dt_from
        return res

    def _date_fin_fn(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for mv_details in self.browse(cr, uid, ids, context=context):
            rang = mv_details.mumero_semain
            if rang == 0:
                msg =  _('the end of the day')
                res[mv_details.id] = msg
            elif rang < 10:
                dt_from = datetime.datetime.now() + datetime.timedelta(days=(7*rang))
                str_dt_from = str(dt_from)[0:10]
                res[mv_details.id] = str_dt_from
            if rang == 10:
                message = _('the remaining time')
                res[mv_details.id] = message
        return res

    _columns = {

              'mumero_semain': fields.integer('Number of week'),
              'sol_product_qty': fields.integer('sol_product_qty'),
              'product_id': fields.many2one('product.product', 'product', required=False),
              'date_debut': fields.function(_date_debut_fn, type='char', string="Start Date"),

              'date_fin': fields.function(_date_fin_fn, type='char', string="End Date"),

              'incoming_qty_week_fn': fields.function(_product_available2,
                                                      
                                                      multi='qty_available_week_fn',
                                                      type='float',
                                                      digits_compute=dp.get_precision('Product Unit of Measure'),
                                                      string='Incoming'),

              'qty_available_week_fn': fields.function(_product_available2,
                                                       multi='qty_available_week_fn',
                                                       type='float',
                                                       digits_compute=dp.get_precision('Product Unit of Measure'),
                                                       string='Quantity in stock',),

              'virtual_available_week_fn': fields.function(_product_available2,
                                                           multi='qty_available_week_fn',
                                                           type='float',
                                                           digits_compute=dp.get_precision('Product Unit of Measure'),
                                                           string='Expected stock',),

              'outgoing_qty_week_fn': fields.function(_product_available2,
                                                      multi='qty_available_week_fn',
                                                      type='float',
                                                      digits_compute=dp.get_precision('Product Unit of Measure'),
                                                      string='Outgoing',),

             }

sol_mv_details()

