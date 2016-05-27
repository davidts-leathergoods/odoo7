# -*- coding: utf-8 -*-
from openerp.osv import osv


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _description = "adding two function to create and update Sale Order Line respecting the right update order" \
                   "of the fields"

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

        sol_id = self.create(cr, uid, values, context={})

        # super method comes from sale_stock.py
        context_product_change = {
            "partner_id": sale_order_brws.partner_id.id,
            "quantity": values['product_uom_qty'],
            "pricelist": sale_order_brws.pricelist_id.id,
            "shop": sale_order_brws.shop_id.id,
            "uom": default_values['product_uom'],
        }

        result = super(sale_order_line, self).product_id_change(cr, uid,
                                                                [sol_id],  # ids
                                                                sale_order_brws.pricelist_id.id,  # pricelist,
                                                                product_brws.id,  # product
                                                                values['product_uom_qty'],  # qty
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
                values[champ] = result['value'][champ]

        self.write(cr, uid, [sol_id], values)

        # method comes from sale.py
        result2 = super(sale_order_line, self).product_uom_change(cr, uid,
                                                                  [sol_id],  # ids
                                                                  sale_order_brws.pricelist_id.id,  # pricelist,
                                                                  product_brws.id,  # product
                                                                  values['product_uom_qty'],  # qty
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
                values[champ] = result2['value'][champ]

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
                result2 = super(sale_order_line, self).product_uom_change(cr, uid,
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
                        values[champ] = result2['value'][champ]

                ret_value = ret_value and self.write(cr, uid, [sale_order_line_brws.id], values)

            if ('product_id' in values or 'product_uom_qty' in values) and ret_value:
                result = super(sale_order_line, self).product_id_change(cr, uid,
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
                        values[champ] = result['value'][champ]

                ret_value = ret_value and self.write(cr, uid, [sale_order_line_brws.id], values)

        return ret_value
