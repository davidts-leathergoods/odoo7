from openerp.osv import fields, osv

class charte(osv.osv):
    _name = 'charte'
    _columns = {
               'name': fields.char('name', size=20, required=True, readonly=False),
              'purchase_order_ids': fields.one2many('purchase.order', 'charte_id', 'Purchase order list', required=False),
             }

charte()

