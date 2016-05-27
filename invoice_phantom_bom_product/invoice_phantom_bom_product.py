# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
        'phantom_prod_invoice' : fields.boolean('Invoice Produce with Phantom BoM', help="It will create Invoice from Delivery Order and take price defined on Sale Order.Useful for product having Phantom BoM.")
    }
    _defaults = {
        'phantom_prod_invoice' : False , 
    }

class stock_invoice_onshipping(osv.osv_memory):
   
    _inherit = "stock.invoice.onshipping"
    _description = "Sale stock Invoice with shipping"
    
    #This method is inherited to create Invoice based on Sale oder line
    def create_invoice(self, cr, uid, ids, context=None):
        
        order_obj = self.pool.get('sale.order')
        picking_obj = self.pool.get('stock.picking')
        active_ids = context.get('active_ids', [])
        onshipdata_obj = self.read(cr, uid, ids, ['journal_id', 'group', 'invoice_date'])
        context['date_inv'] = onshipdata_obj[0]['invoice_date']
        res = {}
        
        for picking in picking_obj.browse(cr, uid, active_ids, context=context):
            if picking.sale_id.phantom_prod_invoice:
                for line in picking.sale_id.order_line :
                    if line.invoiced :
                        line.invoiced = False
                inv_id = order_obj.action_invoice_create(cr, uid, [picking.sale_id.id] ,onshipdata_obj[0]['group'], date_invoice=onshipdata_obj[0]['invoice_date'])
                res[picking.id] = inv_id
        
        if res:
            return res    
        else : 
            return super(stock_invoice_onshipping,self).create_invoice(cr, uid, ids, context)   
        
    
stock_invoice_onshipping()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
