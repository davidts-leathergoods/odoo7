import openerp
import openerp.tools as tools
from openerp.osv import osv
from openerp.osv import fields

class mail_message_wizard(osv.Model):
    _name = 'mail.message.wizard'
    _inherit = 'mail.message'
    _description = 'Attache incoming mail to an object from the selection'

    def send_mail(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        message_id = context.get('default_id', [])
        message = self.pool.get('mail.message').browse(cr, uid, message_id, context = context)
        for wizard in self.browse(cr, uid, ids, context=context):
            object = wizard.object
            if object:
                if  object == 'res.partner_customer':
                    model = 'res.partner'
                    res_id = wizard.customer_id
                elif  object == 'res.partner_supplier':
                    model = 'res.partner'
                    res_id = wizard.supplier_id
                elif  object == 'product.product':
                    model = object
                    res_id = wizard.product_id
                elif  object == 'crm.lead':
                    model = object
                    res_id = wizard.crm_lead_id
                elif  object == 'sale.order':
                    model = object
                    res_id = wizard.sale_order_id
                elif  object == 'purchase.order':
                    model = object
                    res_id = wizard.purchase_order_id
                elif object == 'account.invoice_customer':
                    model = 'account.invoice'
                    res_id = wizard.invoice_customer_id
                elif  object == 'account.invoice_supplier':
                    model = 'account.invoice'
                    res_id = wizard.invoice_supplier_id
                elif  object == 'account.invoice_customer_refund':
                    model = 'account.invoice'
                    res_id = wizard.refund_customer_id
                elif  object == 'account.invoice_supplier_refund':
                    model = 'account.invoice'
                    res_id = wizard.refund_supplier_id
            message.write({'model': model , 'res_id': res_id})
            return {
                'type': 'ir.actions.act_window_close',
            }

    _columns = {
        'object': fields.selection([
                        ('res.partner_customer', 'Customer'),
                        ('res.partner_supplier', 'Supplier'),
                        ('product.product', 'Product'),
                        ('crm.lead', 'Opportunity'),
                        ('sale.order', 'Sale Order'),
                        ('purchase.order', 'Purchase Order'),
                        ('account.invoice_customer', 'Customer Invoice'),
                        ('account.invoice_supplier', 'Supplier Invoice'),
                        ('account.invoice_customer_refund', 'Customer Refund'),
                        ('account.invoice_supplier_refund', 'Supplier Refund'), ], 'Attach To Object' ) ,
        'customer_id': fields.many2one('res.partner','Customer', domain="[('customer','=',True)]" ),
        'supplier_id': fields.many2one('res.partner','Supplier', domain="[('supplier','=',True)]" ),
        'product_id': fields.many2one('product.product','Product' ),
        'crm_lead_id': fields.many2one('crm.lead','Opportunity' ),
        'sale_order_id': fields.many2one('sale.order','Sale Order' ),
        'purchase_order_id': fields.many2one('purchase.order','Purchase Order' ),
        'invoice_customer_id': fields.many2one('account.invoice','Customer Invoice', domain="[('type','=','out_invoice')]"),
        'invoice_supplier_id': fields.many2one('account.invoice','Supplier Invoice', domain="[('type','=','in_invoice')]" ),
        'refund_customer_id': fields.many2one('account.invoice','Customer Refund', domain="[('type','=','out_refund')]"),
        'refund_supplier_id': fields.many2one('account.invoice','Supplier Refund', domain="[('type','=','in_refund')]" ),
    }

    def onchange_model(self, cr, uid, ids, object, customer_id, supplier_id, product_id, crm_lead_id, invoice_customer_id,invoice_supplier_id,sale_order_id,purchase_order_id, refund_customer_id, refund_supplier_id,context=None):
        if object:
            if  object == 'res.partner_customer':
                model = 'res.partner'
                res_id = customer_id
            elif  object == 'res.partner_supplier':
                model = 'res.partner'
                res_id = supplier_id
            elif  object == 'product.product':
                model = object
                res_id = product_id
            elif  object == 'crm.lead':
                model = object
                res_id = crm_lead_id
            elif  object == 'sale.order':
                model = object
                res_id = sale_order_id
            elif  object == 'purchase.order':
                model = object
                res_id = purchase_order_id
            elif object == 'account.invoice_customer':
                model = 'account.invoice'
                res_id = invoice_customer_id
            elif  object == 'account.invoice_supplier':
                model = 'account.invoice'
                res_id = invoice_supplier_id
            elif  object == 'account.invoice_customer_refund':
                model = 'account.invoice'
                res_id = refund_customer_id
            elif  object == 'account.invoice_supplier_refund':
                model = 'account.invoice'
                res_id = refund_supplier_id
        val = {
            'model': model,
            'res_id': res_id,
        }
        return{'value': val}

