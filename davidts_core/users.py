# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _


class ResUsers(osv.osv):

    _inherit = 'res.users'

    _columns = {
        'start_date_period': fields.date("Start date of period"),
        'end_date_period': fields.date("End date of period"),
    }