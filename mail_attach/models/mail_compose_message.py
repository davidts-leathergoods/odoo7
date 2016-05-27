import openerp
import openerp.tools as tools
from openerp.osv import osv
from openerp.osv import fields

class mail_compose_message(osv.Model):
    """ Attache mail from inbox openerp automatically to an object from the selection:
    account.invoice, sale.order, purchase.order and add it to the object chat """
    _inherit = 'mail.compose.message'
    _description = 'Attache mail to an object from the selection'

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

    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        if values.get('object'):
            if  values.get('object') == 'res.partner_customer':
                values['model'] = 'res.partner'
                values['res_id'] = values.get('customer_id')
            elif  values.get('object') == 'res.partner_supplier':
                values['model'] = 'res.partner'
                values['res_id'] = values.get('supplier_id')
            elif  values.get('object') == 'product.product':
                values['model'] = values.get('object')
                values['res_id'] = values.get('product_id')
            elif  values.get('object') == 'crm.lead':
                values['model'] = values.get('object')
                values['res_id'] = values.get('crm_lead_id')
            elif  values.get('object') == 'sale.order':
                values['model'] = values.get('object')
                values['res_id'] = values.get('sale_order_id')
            elif  values.get('object') == 'purchase.order':
                values['model'] = values.get('object')
                values['res_id'] = values.get('purchase_order_id')
            elif values.get('object') == 'account.invoice_customer':
                values['model'] = 'account.invoice'
                values['res_id'] = values.get('invoice_customer_id')
            elif  values.get('object') == 'account.invoice_supplier':
                values['model'] = 'account.invoice'
                values['res_id'] = values.get('invoice_supplier_id')
            elif  values.get('object') == 'account.invoice_customer_refund':
                values['model'] = 'account.invoice'
                values['res_id'] = values.get('refund_customer_id')
            elif  values.get('object') == 'account.invoice_supplier_refund':
                values['model'] = 'account.invoice'
                values['res_id'] = values.get('refund_supplier_id')

        return super(mail_compose_message, self).create(cr, uid, values, context=context)