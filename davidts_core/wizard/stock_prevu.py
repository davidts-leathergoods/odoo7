from openerp.osv import osv

class stock_prevu(osv.osv_memory):
    _name = "stock.prevu"
    _inherit = "sale.order.line"

stock_prevu()

#  vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
