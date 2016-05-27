from openerp.osv import fields, osv
import datetime
import openerp.addons.decimal_precision as dp

def validate_ean14(ean):
    if not ean:
       return True
    if len(ean) <> 14:
        return False
    try:
        int(ean)
    except:
        return False

    eansum = 3 * int(ean[0]) + \
             1 * int(ean[1]) + \
             3 * int(ean[2]) + \
             1 * int(ean[3]) + \
             3 * int(ean[4]) + \
             1 * int(ean[5]) + \
             3 * int(ean[6]) + \
             1 * int(ean[7]) + \
             3 * int(ean[8]) + \
             1 * int(ean[9]) + \
             3 * int(ean[10]) + \
             1 * int(ean[11]) + \
             3 * int(ean[12]);

    eansum = eansum % 10 ;
    eansum = 10 - eansum;
    eansum = eansum % 10
    return (eansum == int(ean[13]))

class product_product(osv.osv):

    _inherit = "product.product"

    def create(self, cr, uid, vals, context=None):
        ids = super(product_product, self).create(cr, uid, vals.copy(), context=context)
        mv_detail_obj = self.pool.get('mv.details')
        sol_mv_detail_obj = self.pool.get('sol.mv.details')
        for i in range(11):
            mv_detail_obj.create(cr, uid, {'mumero_semain': i, 'product_id': ids})
            sol_mv_detail_obj.create(cr, uid, {'mumero_semain': i, 'product_id': ids})
        sol_mv_detail_obj.create(cr, uid, {'mumero_semain': -1, 'product_id': ids})
        return ids

    def _get_reference_prod_template(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = str(product.product_tmpl_id.reference)
        return res

    def _get_old_code(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = str(product.default_code)[1:7] + str(product.default_code)[8:10]
        return res

    def _available_qty(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for product in self.browse(cr, uid, ids, context):
            res[product.id] = product.qty_available + product.outgoing_qty
        return res

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
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
            if f == 'qty_available':
                c.update({ 'states': ('done',), 'what': ('in', 'out') })
            if f == 'virtual_available':
                c.update({ 'states': ('confirmed','waiting','assigned','done'), 'what': ('in', 'out') })
            if f == 'incoming_qty':
                c.update({ 'states': ('confirmed','waiting','assigned'), 'what': ('in',) })
            if f == 'outgoing_qty':
                c.update({ 'states': ('confirmed','waiting','assigned'), 'what': ('out',) })
            stock = self.get_product_available(cr, uid, ids, context=c)
            for id in ids:
                res[id][f] = stock.get(id, 0.0)
        return res

    def _get_next_incoming_date(self, cr, uid, ids, field_name, arg, context):
        res = {}

        for product in self.browse(cr, uid, ids, context=context):
            if context is None:
                context = {}
            location_obj = self.pool.get( 'stock.location' )
            warehouse_obj = self.pool.get( 'stock.warehouse' )
            shop_obj = self.pool.get( 'sale.shop' )

            if not ids:
                ids = self.search( cr, uid, [] )

            if not ids:
                return res

            if context.get( 'shop', False ):
                warehouse_id = shop_obj.read( cr, uid, int( context['shop'] ), ['warehouse_id'] )['warehouse_id'][0]
                if warehouse_id:
                    context['warehouse'] = warehouse_id

            if context.get( 'warehouse', False ):
                lot_id = warehouse_obj.read( cr, uid, int( context['warehouse'] ), ['lot_stock_id'] )['lot_stock_id'][0]
                if lot_id:
                    context['location'] = lot_id

            if context.get( 'location', False ):
                if type( context['location'] ) == type( 1 ):
                    location_ids = [context['location']]
                elif type( context['location'] ) in ( type( '' ), type( u'' ) ):
                    location_ids = location_obj.search( cr, uid, [( 'name', 'ilike', context['location'] )], context = context )
                else:
                    location_ids = context['location']
            else:
                location_ids = []
                wids = warehouse_obj.search( cr, uid, [], context = context )
                if not wids:
                    return res
                for w in warehouse_obj.browse( cr, uid, wids, context = context ):
                    location_ids.append( w.lot_stock_id.id )

            if context.get( 'compute_child', True ):
                child_location_ids = location_obj.search( cr, uid, [( 'location_id', 'child_of', location_ids )] )
                location_ids = child_location_ids or location_ids

            product2uom = {}
            uom_ids = []

            for product1 in self.pool.get( 'product.product' ).read( cr, uid, [product.id], ['uom_id'], context = context ):
                product2uom[product1['id']] = product1['uom_id'][0]
                uom_ids.append( product1['uom_id'][0] )
            uoms_o = {}
            for uom in self.pool.get( 'product.uom' ).browse( cr, uid, uom_ids, context = context ):
                uoms_o[uom.id] = uom

            where = [tuple( location_ids ), tuple( location_ids ), tuple( [product.id] )]

            cr.execute("""SELECT product_id, MIN(date_expected)
                      FROM stock_move st
                      where location_id NOT in %s
                      and location_dest_id in %s
                      and product_id  in %s
                      and state in ( 'confirmed', 'waiting', 'assigned' )
                      and st.date_expected>=CURRENT_DATE
                      GROUP BY product_id""", tuple( where ) )

            results2 = cr.fetchall()

            if results2:
                for prod_id, date_min in results2:
                  res[product.id] = date_min[0:10]
            else :
                res[product.id] = ''
        return res

    def _get_next_incoming_qty(self, cr, uid, ids, field_name, arg, context):
        res = {}

        for product in self.browse(cr, uid, ids, context=context):


            if context is None:
                context = {}
            location_obj = self.pool.get( 'stock.location' )
            warehouse_obj = self.pool.get( 'stock.warehouse' )
            shop_obj = self.pool.get( 'sale.shop' )

            if not ids:
                ids = self.search( cr, uid, [] )

            if not ids:
                return res

            if context.get( 'shop', False ):
                warehouse_id = shop_obj.read( cr, uid, int( context['shop'] ), ['warehouse_id'] )['warehouse_id'][0]
                if warehouse_id:
                    context['warehouse'] = warehouse_id

            if context.get( 'warehouse', False ):
                lot_id = warehouse_obj.read( cr, uid, int( context['warehouse'] ), ['lot_stock_id'] )['lot_stock_id'][0]
                if lot_id:
                    context['location'] = lot_id

            if context.get( 'location', False ):
                if type( context['location'] ) == type( 1 ):
                    location_ids = [context['location']]
                elif type( context['location'] ) in ( type( '' ), type( u'' ) ):
                    location_ids = location_obj.search( cr, uid, [( 'name', 'ilike', context['location'] )], context = context )
                else:
                    location_ids = context['location']
            else:
                location_ids = []
                wids = warehouse_obj.search( cr, uid, [], context = context )
                if not wids:
                    return res
                for w in warehouse_obj.browse( cr, uid, wids, context = context ):
                    location_ids.append( w.lot_stock_id.id )

            if context.get( 'compute_child', True ):
                child_location_ids = location_obj.search( cr, uid, [( 'location_id', 'child_of', location_ids )] )
                location_ids = child_location_ids or location_ids

            product2uom = {}
            uom_ids = []


            for product1 in self.pool.get( 'product.product' ).read( cr, uid, [product.id], ['uom_id'], context = context ):
                product2uom[product1['id']] = product1['uom_id'][0]
                uom_ids.append( product1['uom_id'][0] )
            uoms_o = {}
            for uom in self.pool.get( 'product.uom' ).browse( cr, uid, uom_ids, context = context ):
                uoms_o[uom.id] = uom

            where = [tuple( location_ids ), tuple( location_ids ), tuple( [product.id] )]

            cr.execute("""SELECT product_id, MIN(date_expected)
                      FROM stock_move st
                      where location_id NOT in %s
                      and location_dest_id in %s
                      and product_id  in %s
                      and state in ( 'confirmed', 'waiting', 'assigned' )
                      and st.date_expected>=CURRENT_DATE
                      GROUP BY product_id""", tuple( where ) )

            results2 = cr.fetchall()

            numero_semaine = 0
            if results2:
                for prod_id, date_min in results2:
                  date_min = datetime.datetime.strptime(date_min, '%Y-%m-%d %H:%M:%S')
                  if date_min >  datetime.datetime.now() :
                    while date_min >  datetime.datetime.now() + datetime.timedelta( days = ( 7 * numero_semaine ) ):
                        numero_semaine = numero_semaine + 1

                from_date =  date_min
                to_date = date_min
                where.append( from_date )
                where.append( to_date )

                prodlot_id = context.get( 'prodlot_id', False )
                prodlot_clause = ''
                if prodlot_id:
                    prodlot_clause = ' and st.prodlot_id = %s '
                    where += [prodlot_id]

                cr.execute(
                   'select sum(st.product_qty), st.product_id, st.product_uom '\
                    'from stock_move st '\
                    'where st.location_id NOT IN %s '\
                    'and st.location_dest_id IN %s '\
                    'and st.product_id IN %s '\
                    "and st.state IN ( 'confirmed', 'waiting', 'assigned' )" + "  and  st.date_expected>=%s and st.date_expected<=%s "\
                    + prodlot_clause +
                    'group by st.product_id,st.product_uom', tuple( where ) )

                result_stock_sn = cr.fetchall()
                if result_stock_sn:
                    for stock_incoming,prod_id, prod_uom in result_stock_sn:
                        res[product.id] = stock_incoming
                else :
                    res[product.id] = 0
            else :
                res[product.id] = 0
        return res

    def _get_stock_and_day(self, cr, uid, ids, field_name, arg, context):
        res = {}

        for product in self.browse(cr, uid, ids, context=context):


            if context is None:
                context = {}
            location_obj = self.pool.get( 'stock.location' )
            warehouse_obj = self.pool.get( 'stock.warehouse' )
            shop_obj = self.pool.get( 'sale.shop' )

            if not ids:
                ids = self.search( cr, uid, [] )

            if not ids:
                return res

            if context.get( 'shop', False ):
                warehouse_id = shop_obj.read( cr, uid, int( context['shop'] ), ['warehouse_id'] )['warehouse_id'][0]
                if warehouse_id:
                    context['warehouse'] = warehouse_id

            if context.get( 'warehouse', False ):
                lot_id = warehouse_obj.read( cr, uid, int( context['warehouse'] ), ['lot_stock_id'] )['lot_stock_id'][0]
                if lot_id:
                    context['location'] = lot_id

            if context.get( 'location', False ):
                if type( context['location'] ) == type( 1 ):
                    location_ids = [context['location']]
                elif type( context['location'] ) in ( type( '' ), type( u'' ) ):
                    location_ids = location_obj.search( cr, uid, [( 'name', 'ilike', context['location'] )], context = context )
                else:
                    location_ids = context['location']
            else:
                location_ids = []
                wids = warehouse_obj.search( cr, uid, [], context = context )
                if not wids:
                    return res
                for w in warehouse_obj.browse( cr, uid, wids, context = context ):
                    location_ids.append( w.lot_stock_id.id )

            if context.get( 'compute_child', True ):
                child_location_ids = location_obj.search( cr, uid, [( 'location_id', 'child_of', location_ids )] )
                location_ids = child_location_ids or location_ids

            product2uom = {}
            uom_ids = []


            for product1 in self.pool.get( 'product.product' ).read( cr, uid, [product.id], ['uom_id'], context = context ):
                product2uom[product1['id']] = product1['uom_id'][0]
                uom_ids.append( product1['uom_id'][0] )
            uoms_o = {}
            for uom in self.pool.get( 'product.uom' ).browse( cr, uid, uom_ids, context = context ):
                uoms_o[uom.id] = uom

            where = [tuple( location_ids ), tuple( location_ids ), tuple( [product.id] )]

            prodlot_id = context.get( 'prodlot_id', False )
            prodlot_clause = ''
            if prodlot_id:
                prodlot_clause = ' and st.prodlot_id = %s '
                where += [prodlot_id]

            cr.execute(
               'select sum(st.product_qty), st.product_id, st.product_uom '\
                'from stock_move st '\
                'where st.location_id NOT IN %s '\
                'and st.location_dest_id IN %s '\
                'and st.product_id IN %s '\
                "and st.state IN ( 'confirmed', 'waiting', 'assigned' )" + "  and st.date_expected<=CURRENT_DATE "\
                + prodlot_clause +
                'group by st.product_id,st.product_uom', tuple( where ) )

            result_stock_sn = cr.fetchall()
            if result_stock_sn:
                for stock_incoming,prod_id, prod_uom in result_stock_sn:
                    res[product.id] = stock_incoming
            else :
                res[product.id] = 0

            cr.execute(
               'select sum(st.product_qty), st.product_id, st.product_uom '\
                'from stock_move st '\
                'where st.location_id NOT IN %s '\
                'and st.location_dest_id IN %s '\
                'and st.product_id IN %s '\
                "and st.state IN ( 'done' )" + "  "\
                + prodlot_clause +
                'group by st.product_id,st.product_uom', tuple( where ) )

            result_stock_sn = cr.fetchall()
            if result_stock_sn:
                for stock_incoming,prod_id, prod_uom in result_stock_sn:
                    res[product.id] = res[product.id] + stock_incoming

            cr.execute(
               'select sum(st.product_qty), st.product_id, st.product_uom '\
                'from stock_move st '\
                'where st.location_id  IN %s '\
                'and st.location_dest_id NOT IN %s '\
                'and st.product_id IN %s '\
                "and st.state IN ( 'confirmed', 'waiting', 'assigned' )" + "  and st.date_expected<=CURRENT_DATE "\
                + prodlot_clause +
                'group by st.product_id,st.product_uom', tuple( where ) )

            result_stock_sn = cr.fetchall()
            if result_stock_sn:
                for stock_incoming,prod_id, prod_uom in result_stock_sn:
                    res[product.id] = res[product.id] - stock_incoming

            cr.execute(
               'select sum(st.product_qty), st.product_id, st.product_uom '\
                'from stock_move st '\
                'where st.location_id  IN %s '\
                'and st.location_dest_id NOT IN %s '\
                'and st.product_id IN %s '\
                "and st.state IN ( 'done' )" + "  "\
                + prodlot_clause +
                'group by st.product_id,st.product_uom', tuple( where ) )

            result_stock_sn = cr.fetchall()
            if result_stock_sn:
                for stock_incoming,prod_id, prod_uom in result_stock_sn:
                    res[product.id] = res[product.id] - stock_incoming

        return res

    def _get_qty_ul(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for product_dict in self.browse(cr, uid, ids, context):
            qty_ul = 0.0
            if product_dict.packaging_template:
                for product in product_dict.packaging_template:
                    if product.ul.id == 1:
                        qty_ul=product.qty
            res[product_dict.id]=qty_ul
        return res

    _columns = {
        'available_qty': fields.function(_available_qty, method=True, string='Available quantity', type='float',
                                         size=16),
        'mv_details_ids': fields.one2many('mv.details', 'product_id', 'mv_details', required=False),
        'sol_mv_details_ids': fields.one2many('sol.mv.details', 'product_id', 'sol_mv_details_ids', required=False),
        'reference_prod_template': fields.function(_get_reference_prod_template, type='char',
                                                   string="Reference product template"),
        'old_code': fields.function(_get_old_code, type='char', store=True, string="Old customer reference"),
        'customer_ids': fields.one2many('product.customerinfo', 'product_id', 'Clients'),
        'virtual_available': fields.function(_product_available, multi='qty_available',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity Term',
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored in this location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
        'description_purchase': fields.text('Purchase Description',translate=True),
        'ean' : fields.char('EAN14', size=14,help="The EAN code of the package unit."),

         'next_incoming_qty': fields.function(_get_next_incoming_qty, type='char'),
        'next_incoming_date': fields.function(_get_next_incoming_date, type='char'),
        'stock_end_day':fields.function(_get_stock_and_day, type='char'),
        'qty_ul':fields.function(_get_qty_ul, method=True, type='float', size=16),
    }

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            code = d.get('default_code', False)
            if code:
                name = '[%s]' % (code)
            return d['id'], name
        partner_id = context.get('partner_id', False)
        result = []
        for product in self.browse(cr, user, ids, context=context):
            sellers = filter(lambda x: x.name.id == partner_id, product.seller_ids)
            if sellers:
                for s in sellers:
                    mydict = {
                        'id': product.id,
                        'default_code': s.product_code or product.default_code,
                        'variants': product.variants
                    }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                    'id': product.id,
                    'default_code': product.default_code,
                    'variants': product.variants
                }
                result.append(_name_get(mydict))
        return result
    
    def description_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _description_get(d):
            name = d.get('name', '')
            return d['id'], name
        partner_id = context.get('partner_id', False)
        result = []
        for product in self.browse(cr, user, ids, context=context):
            sellers = filter(lambda x: x.name.id == partner_id, product.seller_ids)
            if sellers:
                for s in sellers:
                    mydict = {
                        'id': product.id,
                        'name': s.product_name or product.name,
                        'variants': product.variants
                    }
                    result.append(_description_get(mydict))
            else:
                mydict = {
                    'id': product.id,
                    'name': product.name,
                    'variants': product.variants
                }
                result.append(_description_get(mydict))
        return result

    def get_search_item_info(self, cr, uid, searchString, partner, limit, context={}):
        result = []
        ids = self.search(cr, uid, ['|',('name', 'ilike', '%'+searchString+'%'), ('default_code', 'ilike', '%'+searchString+'%')], limit=limit, context=context)
        if ids:
            products_info = self.get_items_info(cr, uid, ids, partner, context)
            for id in ids:
                item_infos = products_info[id]
                result.append(item_infos)
        vals = {
                'length': len(result),
                'records': result,
                }
        return vals
    
    def get_item_price(self, cr, uid, product, part, qty, context={}):
        price = 0    
        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        if part.property_product_pricelist:         
            currency = part.property_product_pricelist.currency_id         
            pricelist = part.property_product_pricelist.id         
            date = str(datetime.datetime.now())[0 : 10]
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],product, qty or 1.0, part.id, {
                        'uom': False,
                        'date': date,
                        })[pricelist]
        product = self.browse(cr, uid, product, context=context)         
        std_unit_price = product.list_price  * currency.rate_silent         
        if currency.name == 'GBP':         
            std_unit_price = std_unit_price * 1.06         
         
        if not price > 0:         
            price = product.list_price * currency.rate_silent
                    
        return {'unit_price': price , 'currency': currency.name, 'std_unit_price': std_unit_price or ''}

    def get_item_prices_info(self, cr, uid, product, part, qty, currency, pricelist, context= {}):
        price = 0
        qty_ul = 0.0
        date = str(datetime.datetime.now())[0 : 10]
        if pricelist:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                     product.id, qty or 1.0, part.id, {
                         'uom': False,
                         'date': date,
                         })[pricelist]

            if currency:
                std_unit_price = product.list_price  * currency.rate_silent
                if currency.name == 'GBP':
                    std_unit_price = std_unit_price * 1.06
                if not price > 0:
                    price = product.list_price * currency.rate_silent
                currency = currency.name

        if product.packaging_template:
            for product_tmpl in product.packaging_template:
                if product_tmpl.ul.id == 1:
                    qty_ul=product_tmpl.qty

        return {'unit_price': price , 'currency': currency, 'std_unit_price': std_unit_price or '', 'qty_ul': qty_ul}

    def get_items_info(self, cr, uid, ids, partner, context={}):
        try:
            product_dicts = self.browse(cr, uid, ids, context=context)
            part = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        except:
            return {}
        result = {}
        currency = None
        pricelist = None
        if part.property_product_pricelist:
            currency = part.property_product_pricelist.currency_id
            pricelist = part.property_product_pricelist.id

        for product_dict in product_dicts:
            item_prices = self.get_item_prices_info(cr, uid, product_dict, part, 1, currency, pricelist)
            result.update({product_dict.id: {
                'description': product_dict.name,
                'item': product_dict.default_code,
                'item_id': product_dict.id,
                'std_unit_price': item_prices['std_unit_price'] or '',
                'unit_price': item_prices['unit_price'],
                'currency': item_prices['currency'],
                'stock':product_dict.available_qty,
                'next_incoming_qty':product_dict.next_incoming_qty,
                'next_incoming_date':product_dict.next_incoming_date,
                'stock_forecast':product_dict.virtual_available,
                'qty_ul':item_prices['qty_ul'] or 0.0,
            }})
            
        return result
    
    def get_item_info(self, cr, uid, id, partner, context={}):

        if hasattr(id, '__getitem__'):
            id = id[0]
        try:
            product_dict = self.browse(cr, uid, id, context=context)
            part = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        except:
            return {}

        currency = None
        pricelist = None
        if part.property_product_pricelist:
            currency = part.property_product_pricelist.currency_id
            pricelist = part.property_product_pricelist.id
        linked_items = []
        if product_dict.product_link_ids:
            for product in product_dict.product_link_ids:
                price = self.get_item_prices_info(cr, uid, product.linked_product_id, part, 1, currency, pricelist)['unit_price']
                if not price > 0:
                    price = product.linked_product_id.list_price * currency.rate_silent
                linked_items.append({
                    'ref': product.linked_product_id.reference,
                    'description': product.linked_product_id.name,
                    #'full_description': self.pool.get('product.product').description_get(cr, uid, product.linked_product_id.id),
                    'item': product.linked_product_id.name,
                    'item_id': product.linked_product_id.id,
                    'unit_price': price,
                    'currency': currency.name
                })

        item_prices = self.get_item_prices_info(cr, uid, product_dict, part, 1, currency, pricelist)
        return {
            'description': product_dict.name,
            'full_description': self.pool.get('product.product').description_get(cr, uid, product_dict.id),
            'item': product_dict.default_code,
            'item_id': product_dict.id,
            'std_unit_price': item_prices['std_unit_price'] or '',
            'unit_price': item_prices['unit_price'],
            'linked_items': linked_items,
            'currency': currency.name,
            'stock':product_dict.available_qty,
            'next_incoming_qty':product_dict.next_incoming_qty,
            'next_incoming_date':product_dict.next_incoming_date,
            'stock_forecast':product_dict.virtual_available,
            'qty_ul': item_prices['qty_ul'] or 0.0,
        }


    def _check_ean_key(self, cr, uid, ids, context=None):
        for pack in self.browse(cr, uid, ids, context=context):
            res = validate_ean14(pack.ean)
        return res

    _constraints = [(_check_ean_key, 'Error: Invalid EAN code', ['ean'])]
        
product_product()
