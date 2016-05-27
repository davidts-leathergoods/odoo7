# -*- coding: utf-8 -*- 

from openerp.osv import fields, osv


class res_currency(osv.osv):
    _inherit = "res.currency"

    def compute(self, cr, uid, from_currency_id, to_currency_id, from_amount,
                round=True, currency_rate_type_from=False, currency_rate_type_to=False, context=None):

        #if the flag ax_prices_in_currency is checked, we return the price as it's without conversion
        if context and context.get('ax_prices_in_currency'):
            return from_amount

        return super(res_currency, self).compute(cr, uid, from_currency_id, to_currency_id, from_amount,
                                                   round, currency_rate_type_from, currency_rate_type_to, context)