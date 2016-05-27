# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import os


class crm_claim(osv.osv):
    _name = "crm.claim"
    _inherit = "crm.claim"

    _columns = {
        'crm_claim_prefix': fields.char('SAV prefix', readonly=True),
        'packaging_list_id': fields.many2one('davidts.expedition', 'Packaging List'),
    }

    def create(self, cr, uid, vals, context=None):
        vals['crm_claim_prefix'] = self.pool.get('ir.sequence').get(cr, uid, 'crm.claim')
        ids = super(crm_claim, self).create(cr, uid, vals.copy(), context=context)
        return ids

crm_claim()
