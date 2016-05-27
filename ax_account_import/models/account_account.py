# -*- coding: utf-8 -*- 

from openerp.osv import fields, osv


class MathonAccountOrder(osv.osv):
    _inherit = "account.account"
    _name = _inherit

    _columns = {
               'unused_accounts_prefixe' : fields.boolean('Unused Account have prefix'),
                }