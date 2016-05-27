# -*- coding: utf-8 -*-
from openerp.osv import osv


class sale_order(osv.osv):
    _inherit = "sale.order"
    _description = "Add a public function permetting to create a Sale Order"

    def create_sale_order(self, cr, uid, partner_id, custom_required_fields, context={}):
        """
        Create a sale order for a partner
        :param partner_id:
        :param custom_required_fields:
        :return: created Sale Order ID
        """

        # Models
        partner_obj = self.pool.get('res.partner')

        # we need a default pricelist and fiscal postion
        partner_dict = partner_obj.read(cr, uid, partner_id, context=context)
        price_list_id = partner_dict['property_product_pricelist'][0]
        account_position_id = partner_dict['property_account_position'][0] if partner_dict['property_account_position'] else False

        # standard required fields
        new_sale_order_values = {
            'pricelist_id': price_list_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': partner_id,
            'partner_id': partner_id,
            'fiscal_position': account_position_id
        }

        # add custom required fields
        new_sale_order_values.update(custom_required_fields)

        # create the Sale Order
        sale_order_id = self.create(cr, uid, new_sale_order_values, context=context)
        self.onchange_partner_id(cr, uid, sale_order_id, partner_id, context=context)

        return sale_order_id