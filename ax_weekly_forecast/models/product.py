from openerp.osv import fields, osv
import datetime


class product_product(osv.osv):

    _inherit = "product.product"

    def create(self, cr, uid, vals, context=None):
        ids = super(product_product, self).create(cr, uid, vals.copy(), context=context)
        mv_detail_obj = self.pool.get('mv.details')
        for i in range(13):
            mv_detail_obj.create(cr, uid, {'mumero_semain': i, 'product_id': ids})

        return ids

    def _available_qty(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for id in ids:
            product = self.browse(cr, uid, id, context)
            res[id] = product.qty_available - product.outgoing_qty
        return res

    _columns = {
        'available_qty': fields.function(_available_qty, method=True, string='Available quantity', type='float',
                                         size=16),
        'mv_details_ids': fields.one2many('mv.details', 'product_id', 'mv_details', required=False),

    }




product_product()