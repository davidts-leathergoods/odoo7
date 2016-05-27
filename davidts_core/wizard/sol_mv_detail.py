from openerp.osv import osv

class sol_mv_detail(osv.osv_memory):

    _name = "sol.mv"
    _inherit = "sale.order.line"

sol_mv_detail()
