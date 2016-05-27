# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from datetime import datetime , date
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
import os
from openerp.tools import float_compare
from openerp import SUPERUSER_ID


class DavidtsSalesOrder(osv.osv):

    _inherit = "sale.order"
    
    def _check_sale_order(self, cr, uid, ids, name, args, context=None): 
        cur_obj = self.pool.get('res.currency')
        result = {}
        for o in self.browse(cr, uid, ids):
            result[o.id] = "False"
            amount_untaxed = 0.0
            amount_tax = 0.0 
            amount_total = 0.0
            
            val = val1 = 0.0
            cur = o.pricelist_id.currency_id
            for line in o.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=None)
            amount_tax = cur_obj.round(cr, uid, cur, val)    
            amount_untaxed = cur_obj.round(cr, uid, cur, val1)
            amount_total = amount_untaxed + amount_tax   
           
            if o.credit + amount_total > o.credit_limit:
                result[o.id] = "True"
        return result  
    
    def get_delay_appro(self, cr, uid, ids, name, args, context=None):
        result = {} 
        obj = self.browse(cr, uid, ids[0], context)
        if obj.partner_id:
            result[obj.id] = obj.partner_id.delay_appro or 0
        return result

    def get_warning(self, cr, uid, ids, name, args, context=None):
        result = {}
        obj = self.browse(cr, uid, ids[0], context)
        if obj.partner_id:
            if obj.partner_id.is_company:
                result[obj.id] = obj.partner_id.warning or False
            elif obj.partner_id.parent_id: 
                result[obj.id] = obj.partner_id.parent_id.warning  
            else:
                result[obj.id] = False
        return result

    def _get_ex_work_date(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            if order.requested_date:
                dt = datetime.strptime(order.requested_date, '%Y-%m-%d') - relativedelta(days=order.delay_appro or 0)
                res[order.id] = dt.strftime('%Y-%m-%d')
        return res

    def _get_commitment_date(self, cr, uid, ids, name, arg, context=None):
        res = super(DavidtsSalesOrder, self)._get_commitment_date(cr, uid, ids, name, arg, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            if order.requested_date:
                res[order.id] = order.requested_date
        return res

    def get_credit_limit_message(self, cr, uid, ids, name, args, context=None):
        result = {}
        obj = self.browse(cr, uid, ids[0], context)
        if obj.partner_id:
            result[obj.id] = obj.partner_id.credit_limit or 0
        return result

    def get_credit(self, cr, uid, ids, name, args, context=None):
        result = {}
        obj = self.browse(cr, uid, ids[0], context)
        if obj.partner_id:
            result[obj.id] = obj.partner_id.credit or 0
        return result

    def get_to_invoice_amount(self, partner, cr, uid, context):
        pricelist = partner.property_product_pricelist
        pricelist_obj = self.pool.get('product.pricelist')
        amount = 0.0     
        pikcing_obj = self.pool.get('stock.picking')
        picking_ids = pikcing_obj.search(cr, uid, [('partner_id', '=', partner.id),
                                                   ('type', '=', 'out'),
                                                   ('invoice_state', '=', '2binvoiced')], context=context)
        for pick in pikcing_obj.browse(cr, uid, picking_ids, context=context):
            for line in pick.move_lines:
                product_id = line.product_id
                pricelist = partner.property_product_pricelist.id
                qty = line.product_qty
                price = pricelist_obj.price_get(cr, uid, [pricelist], product_id.id, qty or 1.0, partner.id)[pricelist]
                amount += price*qty
        return amount

    def _get_to_invoice(self, cr, uid, ids, name, args, context=None):
        result = {}
        sales = self.browse(cr, uid, ids, context)
        for sale in sales:
            if sale.partner_id:
                part = self.pool.get('res.partner').browse(cr, uid, sale.partner_id.id, context)
                result[sale.id] = self.get_to_invoice_amount(part, cr, uid, context)
            else:
                result[sale.id] = 0.0    
        return result

    _columns = {
        'warning': fields.function(get_warning, methode=True, type='text', store=True, readOnly=True, string="Warning"),
        'warning_sale_order_limit_credit': fields.function(_check_sale_order, type='char', readonly=True,
                                                           string="warning_sale_order_limit_credit"),
        'credit': fields.function(get_credit, string="Total Receivable"),
        'credit_limit': fields.function(get_credit_limit_message, string="Credit Limit"),
        'delay_appro': fields.function(get_delay_appro, type='integer', string='delay_appro'),
        'ex_work': fields.function(_get_ex_work_date, string="Ex-work Date", type='date', store=True),
        'to_invoice': fields.function(_get_to_invoice, string='To invoice'),
        'order_policy': fields.selection([('picking', 'On Delivery Order'),
                                          ('manual', 'On Demand'),
                                          ('prepaid', 'Before Delivery')],
                                         'Create Invoice', required=True, readonly=True,
                                         help="""On demand: A draft invoice can be created from the sales order when
                                         needed. \nOn delivery order: A draft invoice can be created from the delivery
                                         order when the products have been delivered. \nBefore delivery: A draft invoice
                                         is created from the sales order and must be paid before the products can
                                         be delivered."""),
        'commitment_date': fields.function(_get_commitment_date, store=True, type='date', string='Commitment Date', help="Committed date for delivery."),
        'state': fields.selection([('draft', 'Draft Quotation'),
                                   ('to_confirm', 'To confirm'),
                                   ('sent', 'Quotation Sent'),
                                   ('cancel', 'Cancelled'),
                                   ('waiting_date', 'Waiting Schedule'),
                                   ('progress', 'Sales Order'),
                                   ('manual', 'Sale to Invoice'),
                                   ('shipping_except', 'Shipping Exception'),
                                   ('invoice_except', 'Invoice Exception'),
                                   ('done', 'Done')],
                                  'Status', readonly=True, select=True),
    }

    _defaults = {
        'order_policy': 'picking',
    }

    def action_quotation_to_confirm(self, cr, uid, ids, context=None):
        """Ajout d'un workflow"""
        return self.write(cr, uid, ids, {'state': 'to_confirm'})

    def action_quotation_draft(self, cr, uid, ids, context=None):
        """Ajout d'un workflow"""
        return self.write(cr, uid, ids, {'state': 'draft'})

    def action_button_confirm(self, cr, uid, ids, context=None):
        result = super(DavidtsSalesOrder, self).action_button_confirm(cr, uid, ids, context=context)
        where = []
        cr.execute("COMMIT;", tuple(where))
        for id in ids:
            cr.execute("select id from stock_picking where sale_id=%d" % id)
            picking_ids = [x[0] for x in cr.fetchall()]
            if picking_ids:
                for picking_id in picking_ids:
                    PATH_JOB = '../../project_addons/openerp_wms/sale_openerpwms/sale_openerpwms/sale_openerpwms_run.sh'
                    if self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.path_openerp_wms"):
                        os.system('sh ' + PATH_JOB + " " + str(picking_id))
            else:
                raise osv.except_osv(_('Warning!'), _('WMS files can not be generate. Please specify WMS_files generated path from OpenERP (Settings => Sales => Davidts => Path: WMS files generated)'))
        return result
    
    def onchange_shop_id(self, cr, uid, ids, shop_id, context=None):
        res = super(DavidtsSalesOrder, self).onchange_shop_id(cr, uid, ids, shop_id, context=context)
        if shop_id == 1:
            if res.get('value'):
                value = res.get('value')
                if value.get('pricelist_id'):
                    del res['value']['pricelist_id']
        return res

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        result = super(DavidtsSalesOrder, self).onchange_partner_id(cr, uid, ids, part, context=context)
        obj = self.pool.get('res.partner').browse(cr, uid, part, context=None)
        if obj.id:
            cr.execute("select id from res_partner "
                       "where parent_id = %s and type='delivery' "
                       "group by id order by Min(shipping_adress_sequence)", (obj.id,))
            res = cr.fetchone() or obj.id
        else:
            return True
        if part:
            credit_limit = obj.credit_limit or 0
            credit = obj.credit or 0
            section_id = obj.section_id.id or False
            if obj.is_company:
                warning = obj.warning or False
            elif obj.parent_id:
                warning = obj.parent_id.warning or False
            else:
                warning = False

            partner_shipping_id = res
            result['value']['partner_shipping_id'] = partner_shipping_id
            result['value']['credit_limit'] = credit_limit
            result['value']['credit'] = credit
            result['value']['warning'] = warning
            result['value']['delay_appro'] = obj.delay_appro or 0
            result['value']['section_id'] = section_id
        return result

    def button_update_price_product(self, cr, uid, ids, context=None):
        obj_sale_line = self.pool.get('sale.order.line')
        pricelist_obj = self.pool.get('product.pricelist')
        sale_order = self.browse(cr, uid, ids[0], context)

        cr.execute("select  product_tmpl_id,sum(product_uom_qty)as sum_qty, 0 as price_unit from product_product p \
            inner join sale_order_line sol \
            on p.id = sol.product_id \
            where sol.order_id = %s \
            GROUP BY p.product_tmpl_id", (sale_order.id,))
        res = cr.dictfetchall()

        list_article_temp = []
        qty = 0
        for line in sale_order.order_line:
            product = line.product_id
            product_template_id = product.product_tmpl_id.id
            if product_template_id not in list_article_temp:
                for r in res:
                    if r['product_tmpl_id'] == product_template_id:
                        qty = r['sum_qty']
                        price = pricelist_obj.price_get(cr, uid, [sale_order.pricelist_id.id], product.id, qty or 1.0,
                                                        sale_order.partner_id.id, {})[sale_order.pricelist_id.id]
                        list_article_temp.append(product_template_id)
                        r['price_unit'] = price
            else:
                    for r in res:
                        if r['product_tmpl_id'] == product_template_id:
                            price = r['price_unit']
            obj_sale_line.write(cr, uid, [line.id], {'price_unit': price})
        return res

    def check_order_to_confirm(self, cr, uid, ids=None, context=None):
        picking_obj = self.pool.get('stock.picking.out')
        if not ids:
            cr.execute("select id from sale_order where state not in ('done', 'cancel', 'draft') order by id")
            ids = [x[0] for x in cr.fetchall()]
        if ids:
            for id in ids:
                cr.execute("select id from stock_picking where type='out' and sale_id=%d" % id)
                picking_ids = [x[0] for x in cr.fetchall()]
                if picking_ids:
                    confirm = True
                    for picking_id in picking_ids:
                        if picking_obj.browse(cr, uid, picking_id, context).invoice_state == "2binvoiced":
                            confirm = False
                            break
                    if confirm:
                        self.write(cr, uid, [id], {'state': 'done'})
        return True


    def get_order_info(self, cr, uid, id, context={}):

        if hasattr(id, '__getitem__'):
            id = id[0]

        # noinspection PyBroadException
        try:
            sale_order_dict = self.browse(cr, uid, id, context=context)
        except:
            return {}
        partner = sale_order_dict.partner_id
        # we build contacts list
        shipping_partner = sale_order_dict.partner_shipping_id
        shipping_addresses = {
            'ref':   shipping_partner.id,
            'name': shipping_partner.name,
            'address': {
                 'city': shipping_partner.city,
                 'country': shipping_partner.country.name,
                 'zipCode': shipping_partner.zip,
                 'street': filter(None, [shipping_partner.street, shipping_partner.street2])
            }
        }

        line_ids = []
        for line in sale_order_dict.order_line:
            line_ids.append(line.id)

        lines = []
        for line in sale_order_dict.order_line:
            value = {
            'line_id': line.id,
            'description': line.name,
            'item': line.product_id.default_code,
            'item_id': line.product_id.id,
            'qty': line.product_uom_qty,
            'price_unit':line.price_unit,
            'total': line.price_subtotal,
            'stock': line.product_id.available_qty,
             }
            if line.price_unit != 0:
                value['unit_price'] = line.price_unit
            else :
                value['unit_price'] = line.product_id.list_price
            lines.append(value)

        customer = {
            'address': {
                'city': partner.city,
                'country': partner.country.name,
                'zipCode': partner.zip,
                'street': filter(None, [partner.street, partner.street2])
            },
            'shipping_address': shipping_addresses,
            'cust_id': partner.id,
            'email': partner.email,
            'fax': partner.fax,
            'name': partner.name,
            'tel': partner.phone,
            'vat': partner.vat,
        }

        if sale_order_dict.note:
            note = sale_order_dict.note
        else:
            note = ''
        return {
            'comments': note,
            'requested_date': sale_order_dict.requested_date or '',
            'order_id': sale_order_dict.id,
            'currency': sale_order_dict.pricelist_id.currency_id.name,
            'pricelist': sale_order_dict.pricelist_id.name,
            'order_number': sale_order_dict.name,
            'customer_ref': sale_order_dict.client_order_ref,
            'status': sale_order_dict.state,
            'total_amount': sale_order_dict.amount_total,
            'date': sale_order_dict.date_order,
            'hvat_amount': sale_order_dict.amount_untaxed,
            'vat_amount': sale_order_dict.amount_tax,
            'line_items': line_ids,
            'lines': lines,
            'customer': customer
        }


    def create_and_update_prices(self, cr, uid, values, context={}):

        if not values.get('shop_id', False):
            # we retrieve default values
            fields_to_default = [
                'shop_id',
            ]
            default_values = self.default_get(cr, uid, fields_to_default)
            values['shop_id'] = default_values['shop_id']


        update_values = self.onchange_partner_id(cr, uid, [], values['partner_id'], context=context)
        if 'partner_invoice_id' not in values:
                values['partner_invoice_id']=update_values['value']['partner_invoice_id']
        if 'partner_shipping_id' not in values:
                values['partner_shipping_id']=update_values['value']['partner_shipping_id']
        if 'pricelist_id' not in values:
                values['pricelist_id']=update_values['value']['pricelist_id']


        so_id = super(DavidtsSalesOrder, self).create(cr, uid, values, context=context)
        if not so_id:
            return None

        update_values = self.onchange_partner_id(cr, uid, [so_id], values['partner_id'], context=context)
        for champ in update_values['value']:
            if (not champ in values) or ((champ in values) and values.get(champ) == 'false'):
                values[champ]= update_values['value'][champ]


        if not self.write(cr, uid, so_id, values, context=context):
            return None

        return so_id


    def  send_mail_automatique(self, cr, uid, ids, context=None):

        if type(ids) is not list:
            ids = [ids]
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'davidts_core', 'email_template_edi_sale_tablet')[1]
            #template_id = 15
        except ValueError:
            template_id = False

        mail_obj = self.pool.get('mail.compose.message')
        onchange_template_id_value = mail_obj.onchange_template_id(cr,uid,[],template_id = template_id ,composition_mode ='comment',model = 'sale.order',res_id = ids[0],context=context)

        list_partner_ids = []
        sale_brow = self.browse(cr, uid, ids[0], context)
        create_uid = sale_brow.user_id.partner_id.id
        company_id = sale_brow.company_id.partner_id.id
        list_partner_ids.append(create_uid)
        list_partner_ids.append(company_id)

     #   list_partner_ids = onchange_template_id_value['value']['partner_ids']
        onchange_template_id_value['value']['partner_ids'] =[[6, False, list_partner_ids]]

        attachment_ids = []
        for champ in onchange_template_id_value['value']['attachment_ids']:
            attachment_ids.append([4, champ, False])

        onchange_template_id_value['value']['attachment_ids'] =attachment_ids

        values = onchange_template_id_value['value']

        values['template_id'] = template_id
        values['composition_mode'] = 'comment'
        values['res_id'] = ids[0]
        values['model'] = 'sale.order'

        ctx = {
            'default_model': 'sale.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        }

        mail_id = mail_obj.create(cr, uid, values, ctx)
        result = mail_obj.send_mail(cr, SUPERUSER_ID, [mail_id], context=ctx)
        self.write(cr, uid, ids, {'state': 'to_confirm'})
        return result

DavidtsSalesOrder()
 

class DavidtsSalesOrderLine(osv.osv):

    _inherit = "sale.order.line"

    def getlistprice(self, cr, uid, ids, context=None):
        obj_sale_order_line = self.browse(cr, uid, ids[0], context)
        product = obj_sale_order_line.product_id.id
        partner = obj_sale_order_line.order_id.partner_id.id
        qty = obj_sale_order_line.product_uom_qty
        pricelist = obj_sale_order_line.order_id.pricelist_id.id
        price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                                                             product, qty or 1.0, partner, {})[pricelist]
        return price

    def _get_list_price(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj_sale_order_line = self.browse(cr, uid, ids[0], context)
        obj_sale_order = obj_sale_order_line.order_id
        l = len(ids)
        if l > 1:
            for line in obj_sale_order.order_line:
                price = line.getlistprice()
                res[line.id] = price
        if len(ids) == 1:
            price = obj_sale_order_line.getlistprice()
            res[obj_sale_order_line.id] = price   
        return res

    _columns = {
        'product_uos_qty': fields.float('Quantity (UoS)', digits=(6, 0), readonly=True,
                                        states={'draft': [('readonly', False)]}),
        'product_uom_qty': fields.float('Quantity', digits=(6, 0), required=True, readonly=True,
                                        states={'draft': [('readonly', False)]}),
        'price_unit_for_list_price': fields.float('List price 2'),
        'list_price2': fields.float('List Price', readonly=True),
    }
    _defaults = {
        'list_price2': 0.0,
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('price_unit_for_list_price'):
            vals['list_price2'] = vals.get('price_unit_for_list_price')
        return super(DavidtsSalesOrderLine, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('price_unit_for_list_price'):
            vals['list_price2'] = vals.get('price_unit_for_list_price')
        return super(DavidtsSalesOrderLine, self).write(cr, uid, ids, vals, context)

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):

        product_obj = self.pool.get('product.product')

        result = super(DavidtsSalesOrderLine, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom,
                                                                      qty_uos, uos, name, partner_id, lang, update_tax,
                                                                      date_order, packaging, fiscal_position, flag,
                                                                      context)
        if result.get('warning'):
            del result['warning']

        if product:
            if result.get('value'):
                value = result.get('value')
                if value.get('price_unit'):
                    result['value']['list_price2'] = value.get('price_unit') or 0.0
                    result['value']['price_unit_for_list_price'] = value.get('price_unit') or 0.0

            current_product = product_obj.browse(cr, uid, product, context=context)
            if not flag:
                result['value']['name'] = product_obj.description_get(cr, uid, [current_product.id], context=context)[0][1]
                if current_product.description_sale:
                    result['name'] += '\n'+current_product.description_sale

        return result

    def create_and_update_prices(self, cr, uid, values, context={}):
        """
        Create and update prices
        :param cr:
        :param uid:
        :param values: Must contain order_id, product_id, name, product_uom_qty
        :param context:
        :return:
        """
        # required paremeters:
        #  - order_id
        #  - product_id
        #  - product_uom_qty (sty)
        #
        sale_order_obj = self.pool.get('sale.order')
        sale_order_brws = sale_order_obj.browse(cr, uid, values['order_id'], context)
        product_brws = self.pool.get('product.product').browse(cr, uid, values['product_id'], context)

        # we retrieve default values
        fields_to_default = [
            'product_uom',
            'discount',
            'product_uom_qty',
            'product_uos_qty',
            'state',
        ]
        default_values = self.default_get(cr, uid, fields_to_default)

        #
        sol_id = self.create(cr, uid, values, context={})

        # super method comes from sale_stock.py
        context_product_change = {
            "partner_id": sale_order_brws.partner_id.id,
            "quantity": values['product_uom_qty'],
            "pricelist": sale_order_brws.pricelist_id.id,
            "shop": sale_order_brws.shop_id.id,
            "uom": default_values['product_uom'],
        }

        result = super(DavidtsSalesOrderLine, self).product_id_change(cr, uid,
                                                                      [sol_id],                         # ids
                                                                      sale_order_brws.pricelist_id.id,  # pricelist,
                                                                      product_brws.id,                  # product
                                                                      values['product_uom_qty'],        # qty
                                                                      # args end
                                                                      uom=default_values['product_uom'],
                                                                      qty_uos=default_values['product_uos_qty'],
                                                                      uos=default_values['product_uom'],
                                                                      name=product_brws.name_template,
                                                                      partner_id=sale_order_brws.partner_id.id,
                                                                      lang=False,
                                                                      update_tax=True,
                                                                      date_order=sale_order_brws.date_order,
                                                                      packaging=False,
                                                                      fiscal_position=sale_order_brws.fiscal_position.id,
                                                                      flag=False,
                                                                      context=context_product_change)


        # product_id_returns a tax array we must transform to write.
        result['value']['tax_id'] = [(6, 0, result['value']['tax_id'])]

        for champ in result['value']:
            if (not champ in values) or ((champ in values) and values.get(champ) == 'false'):
                values[champ]= result['value'][champ]

        self.write(cr, uid, [sol_id], values)

        # method comes from sale.py
        result2 = super(DavidtsSalesOrderLine, self).product_uom_change(cr, uid,
                                                                        [sol_id],                         # ids
                                                                        sale_order_brws.pricelist_id.id,  # pricelist,
                                                                        product_brws.id,                  # product
                                                                        values['product_uom_qty'],        # qty
                                                                        # args end
                                                                        uom=default_values['product_uom'],
                                                                        qty_uos=default_values['product_uos_qty'],
                                                                        uos=default_values['product_uom'],
                                                                        name=product_brws.name_template,
                                                                        partner_id=sale_order_brws.partner_id.id,
                                                                        lang=False,
                                                                        update_tax=True,
                                                                        date_order=sale_order_brws.date_order,
                                                                        context={})


        for champ in result2['value']:
            if (not champ in values) or ((champ in values) and values.get(champ) == 'false'):
                values[champ]= result2['value'][champ]

        self.write(cr, uid, [sol_id], values)

        return sol_id

    def write_and_update_prices(self, cr, uid, ids, values, context={}):
        """
        Create and update prices
        :param cr:
        :param uid:
        :param ids: ids of lines to update
        :param values: Must contain product_id, name, product_uom_qty
        :param context:
        :return:
        """
        # required paremeters:
        #  - order_id
        #  - product_id
        #  - product_uom_qty (qty)
        #
        ret_value = self.write(cr, uid, ids, values, context=context)

        for sale_order_line_brws in self.browse(cr, uid, ids, context=context):
            sale_order_brws = sale_order_line_brws.order_id
            if 'product_uom' in values:
                # method comes from sale.py
                result2 = super(DavidtsSalesOrderLine, self).product_uom_change(cr, uid,
                                                                                [sale_order_brws.id],             # ids
                                                                                sale_order_brws.pricelist_id.id,  # pricelist,
                                                                                values.get('product_id', False) or sale_order_line_brws.product_id.id,  # product
                                                                                values.get('product_uom_qty', False) or sale_order_line_brws.product_uom_qty,  # qty
                                                                                # args end
                                                                                uom=values.get('product_uom', False) or sale_order_line_brws.product_uom.id,
                                                                                qty_uos=values.get('product_uos_qty', False) or sale_order_line_brws.product_uos_qty,
                                                                                #TODO: Comprendre pourquoi on met ca
                                                                                uos=values.get('product_uos', False) or sale_order_line_brws.product_uos.id,
                                                                                name=values.get('name', False) or sale_order_line_brws.name,
                                                                                partner_id=sale_order_brws.partner_id.id,
                                                                                lang=False,
                                                                                update_tax=True,
                                                                                date_order=sale_order_brws.date_order,
                                                                                context={})


                for champ in result2['value']:
                   if (not champ in values) or ((champ in values) and values.get(champ) == 'false'):
                       values[champ]= result2['value'][champ]

                ret_value = ret_value and self.write(cr, uid, [sale_order_line_brws.id], values)

            if ('product_id' in values or 'product_uom_qty' in values) and ret_value:
                result = super(DavidtsSalesOrderLine, self).product_id_change(cr, uid,
                                                                              [sale_order_brws.id],             # ids
                                                                              sale_order_brws.pricelist_id.id,  # pricelist,
                                                                              values.get('product_id', False) or sale_order_line_brws.product_id.id,  # product
                                                                              values.get('product_uom_qty', False) or sale_order_line_brws.product_uom_qty,  # qty
                                                                              # args end
                                                                              uom=values.get('product_uom', False) or sale_order_line_brws.product_uom.id,
                                                                              qty_uos=values.get('product_uos_qty', False) or sale_order_line_brws.product_uos_qty,
                                                                              uos=values.get('product_uos', False) or sale_order_line_brws.product_uos.id,
                                                                              name=values.get('name', False) or sale_order_line_brws.name,
                                                                              partner_id=sale_order_brws.partner_id.id,
                                                                              lang=False,
                                                                              update_tax=True,
                                                                              date_order=sale_order_brws.date_order,
                                                                              packaging=False,
                                                                              fiscal_position=sale_order_brws.fiscal_position.id,
                                                                              flag=False,
                                                                              context={})
                                                                              #context=context_product_change)


                if result['value'].get('tax_id', False):
                    # product_id_returns a tax array we must transform to write.
                    result['value']['tax_id'] = [(6, 0, result['value']['tax_id'])]


                for champ in result['value']:
                    if (not champ in values) or ((champ in values) and values.get(champ) == 'false'):
                        values[champ]= result['value'][champ]

                ret_value = ret_value and self.write(cr, uid, [sale_order_line_brws.id], values)

        return ret_value

DavidtsSalesOrderLine()
