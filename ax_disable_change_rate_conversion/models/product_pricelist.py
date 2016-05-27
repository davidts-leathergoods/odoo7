# -*- coding: utf-8 -*- 

from openerp.osv import fields, osv


class product_pricelist(osv.osv):
    _inherit = "product.pricelist"

    def price_get(self, cr, uid, ids, prod_id, qty, partner=None, context=None):
        if context is None:
            context = {}

        #in our logic we assume that even if the core code consider that we can have multiple pricelist
        #in practice this seems impossible, so we inject here our flag value that we will use in the compute
        #function. If we are wrong, we will have to override the price_get_multi function instead of this one
        assert len(ids) == 1, "Only one pricelist is permitted"

        cr.execute("SELECT ax_prices_in_currency FROM product_pricelist WHERE id IN %s", (tuple(ids),))
        pricelist_ax_prices_in_currency = cr.fetchone()[0]

        context.update({'ax_prices_in_currency': pricelist_ax_prices_in_currency})

        result = super(product_pricelist, self).price_get(cr, uid, ids, prod_id, qty, partner=partner, context=context)

        return result

    _columns = {
        'ax_prices_in_currency': fields.boolean('Prices in currency',
                    help="If checked, discount will be applied but price won't be converted to the company currency."),
    }