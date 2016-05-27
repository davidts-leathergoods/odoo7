# -*- coding: utf-8 -*-
from openerp.osv import fields, osv


class CtSaleObjective(osv.osv):
    _name = "ct_sale_objective"
    _description = "model used in jasper training 20/11/2014"
    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'objective': fields.float('Objective'),
        }