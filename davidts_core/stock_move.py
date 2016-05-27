# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
# Evolution #45407
class StockPicking(osv.osv):
    _inherit = 'stock.move'
    
    def _set_expected_date(self, cr, uid, ids, name, value, arg, context=None):
        sale_obj = self.pool.get('sale.order')
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.origin:
                sale_ids = sale_obj.search(cr, uid, [('name', '=', line.origin)])
                if sale_ids:
                    sale = sale_obj.browse(cr, uid, sale_ids[0])
                    if sale.commitment_date:
                        result[line.id]=sale.commitment_date
        return result
    
    _columns = {    
        'wms_qty': fields.float('WMS Quantity'),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True, domain=[('type','<>','service')],states={'done': [('readonly', False)]}),
        'product_qty': fields.float('Quantity',digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True,states={'done': [('readonly', False)]},
            help="This is the quantity of products from an inventory "
                "point of view. For moves in the state 'done', this is the "
                "quantity of products that were actually moved. For other "
                "moves, this is the quantity of product that is planned to "
                "be moved. Lowering this quantity does not generate a "
                "backorder. Changing this quantity on assigned moves affects "
                "the product reservation, and should be done with care."
        ),
       'date_expected': fields.function(_set_expected_date,string='Scheduled Date',store= True,type='datetime',help="Scheduled date for the processing of this move"),

}
    
    
    