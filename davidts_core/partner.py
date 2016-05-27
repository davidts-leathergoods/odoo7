#encoding: utf8
from openerp.osv import fields, osv


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'


    def _fields_sync(self, cr, uid, partner, update_values, context=None):
        if update_values.get('parent_id'):
            if partner.parent_id:
                vals = self.onchange_parent_id(cr, uid,[], partner.parent_id.id)
                partner.write(vals['value'])

        return super(res_partner, self)._fields_sync( cr, uid, partner, update_values, context)

    _columns = {
        'contact_type_id': fields.many2one('davidts.contact_type', 'type'),
        'responsible': fields.char('Responsable', size=32),
        'credit_limit_date': fields.date('Date limite de credit'),
        'warning': fields.char('Warning', size=64),
        'prompt_payment_discount_rate': fields.float("Discount rate"),
        'shipping_adress_sequence': fields.integer("Numero de sequence"),
        'sageecommerce': fields.char('sageecommerce', size=32),
        'pwecommerce': fields.char('pwecommerce', size=32),
        #Taux d'escompte client
        'taux_escompte': fields.float('Discount rate'),
        'delay_appro': fields.integer('Delay appro'),
    }
    _defaults = {
        'shipping_adress_sequence': 5,
    }



    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            if record.zip and record.city:
                name = "%s, (%s, %s)" % (record.name, record.zip, record.city)
            else: 
                name = record.name
            name_partner = record.name
            if record.parent_id and not record.is_company:
                if record.type:
                    name = "%s, %s, %s" % (record.parent_id.name, name_partner, record.type)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n', '\n')
                name = name.replace('\n\n', '\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name)) 
        return res


    def get_customer_pricelist(self, cr, uid, id, context={}):   

        if hasattr(id, '__getitem__'):
            id = id[0]

        # noinspection PyBroadException
        try:
            res_partner_dict = self.browse(cr, uid, id, context=context)
        except:
            return {}


        return {
            'pricelist' : res_partner_dict.property_product_pricelist.id
        }

    def get_customer_full_info(self, cr, uid, id, context={}):
        """
        Returns an "information full" customer object as required by tablet proxy

        :param cr: Current transaction cursor.
        :type cr: openerp.sql_db.Cursor
        :param uid: The user executing the transaction
        :type uid: int
        :param id: The customer we must provide information about
        :param context:
        :type context: dict
        :return: an "information full" customer object as required by tablet proxy or an empty dict if customer does not exist.
        :rtype: dict
        """
        # We process only 1 customer per call ; the first if user passed several
        if hasattr(id, '__getitem__'):
            id = id[0]

        # noinspection PyBroadException
        try:
            res_partner_dict = self.browse(cr, uid, id, context=context)
        except:
            return {}

        # we build contacts list
        contacts_list = [{
            'email': child.email,
            'last_name': child.name,
            'phone': child.phone or child.mobile,
            'title': child.function,
        } for child in res_partner_dict.child_ids if child.type == 'contact']

        # we build sale orders dict
        sale_orders_list = [{
            'date': order.date_order,
            'total_amount': order.amount_total,
            'order_id': order.id,
            'order_number': order.name,
            'status': order.state
        } for order in res_partner_dict.sale_order_ids if order.state not in ['draft','cancel']]


        shipping_addresses_list = [{}]
        cr.execute("select id from res_partner "
                       "where parent_id = %s and type='delivery' "
                       "group by id order by Min(shipping_adress_sequence)", (res_partner_dict.id,))
        res = cr.fetchone() or [res_partner_dict.id]

        if res and res[0]:
            res = res[0]
        for child in res_partner_dict.child_ids :
            if child.id == res and  child.type == 'delivery':
                shipping_addresses_list[0] = {
                'ref': child.id,
                'name': child.name,
                'address' : {
                        'city': child.city,
                        'country': child.country.name,
                        'zipCode': child.zip,
                        'street': filter(None, [child.street, child.street2])
                    }
                }

        for child in res_partner_dict.child_ids :
            if child.id != res and  child.type == 'delivery':
                shipping_addresses_list.append( {
                'ref': child.id,
                'name': child.name,
                'address' : {
                        'city': child.city,
                        'country': child.country.name,
                        'zipCode': child.zip,
                        'street': filter(None, [child.street, child.street2])
                    }
                })

        pricelist_id = ''
        pricelist_name = ''
        if res_partner_dict.property_product_pricelist:
            pricelist_id = res_partner_dict.property_product_pricelist.id
            pricelist_name = res_partner_dict.property_product_pricelist.name

        return {
            'address': {
                'city': res_partner_dict.city,
                'country': res_partner_dict.country.name,
                'zipCode': res_partner_dict.zip,
                'street': filter(None, [res_partner_dict.street, res_partner_dict.street2])
            },
            'pricelist':{'id': pricelist_id ,'name': pricelist_name},
            'category': res_partner_dict.category_id[0].name if res_partner_dict.category_id else None,
            'commercial_contact':{ "last_name": res_partner_dict.user_id.name if res_partner_dict.user_id else None },
            'commercial_team': res_partner_dict.section_id.name if res_partner_dict.section_id else None,
            'contacts': contacts_list,
            'credit_limit': res_partner_dict.credit_limit,
            'cust_id': id,
            'email': res_partner_dict.email,
            'fax': res_partner_dict.fax,
            'in_order_amount': res_partner_dict.credit,
            'name': res_partner_dict.display_name,
            'orders': sale_orders_list,
            'phone': res_partner_dict.phone or res_partner_dict.mobile,
            'vat': res_partner_dict.vat,
            'shipping_addresses': shipping_addresses_list,
            'default_currency' : res_partner_dict.property_product_pricelist.currency_id.name,
        }

    
    def onchange_parent_id(self, cr, uid,ids,  parent_id):
        if not parent_id:
            return {}
        parent = self.browse(cr, uid, parent_id)
        val = {
            'user_id': parent.user_id.id or False,
            'section_id': parent.section_id.id or False,
        }

        return{'value': val}


class DavidtsContactType(osv.osv):

    _name = 'davidts.contact_type'

    _columns = {
        'name': fields.char('Type'),
    }
