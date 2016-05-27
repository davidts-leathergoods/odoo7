# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class order_configuration(osv.osv_memory):
    _inherit = 'sale.config.settings'
    _columns = {
        'module_order_mode_line': fields.boolean("Order Mode line"),
        'group_invoice_deli_orders': fields.boolean('Generate invoices after and based on delivery orders',
            implied_group='sale_stock.group_invoice_deli_orders', readonly=True,
            help="To allow your salesman to make invoices for Delivery Orders using the menu 'Deliveries to Invoice'."),
        'prompt_payment_discount_rate': fields.float("Taux d'escompte"),
        'default_picking_policy': fields.boolean("Deliver all at once when all products are available.",
                  help="Sales order by default will be configured to deliver all products at once instead of delivering each product when it is available. This may have an impact on the shipping price."),
        'path_openerp_wms': fields.char("WMS files generated path"),
        'path_wms_openerp_sale': fields.char("Read WMS sale files path"),
        'path_wms_openerp_purchase': fields.char("Read WMS purchase files path"),
        'wmsfiles_after_treated': fields.char("Drop files after processing"),
        'host': fields.char("Hôte"),
        'port': fields.integer("Port"),
        'user': fields.char("User"),
        'password': fields.char("Password"),
        'db_name': fields.char("Database"),
    }
    _defaults = {
                'port': 22,
        'default_order_policy': 'picking',
    }  #  Begin Evolution #45339
    def get_default_prompt_payment_discount_rate(self, cr, uid, fields, context=None):
        discount = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.prompt_payment_discount_rate") or "0"
        return {'prompt_payment_discount_rate': float(discount),}

    def set_prompt_payment_discount_rate(self, cr, uid, ids, context=None):
        discount = self.browse(cr, uid, ids[0], context)["prompt_payment_discount_rate"] or ""
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.prompt_payment_discount_rate", discount)
        
    #  End Evolution #45339
    #Begin Evolution #47014
    def get_default_path_openerp_wms(self, cr, uid, fields, context=None):
        file = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.path_openerp_wms") or ""
        return {'path_openerp_wms': file,}

    def set_path_openerp_wms(self, cr, uid, ids, context=None):
        file = self.browse(cr, uid, ids[0], context)["path_openerp_wms"] or ""
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.path_openerp_wms", file)
    #End Evolution #47014 
    #Begin Evolution #47021path_wms_openerp
    def get_default_path_wms_openerp_sale(self, cr, uid, fields, context=None):
        file = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.path_wms_openerp_sale") or ""
        return {'path_wms_openerp_sale': file,}

    def set_path_wms_openerp_sale(self, cr, uid, ids, context=None):
        file = self.browse(cr, uid, ids[0], context)["path_wms_openerp_sale"] or ""
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.path_wms_openerp_sale", file)

    def get_default_path_wms_openerp_purchase(self, cr, uid, fields, context=None):
        file = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.path_wms_openerp_purchase") or ""
        return {'path_wms_openerp_purchase': file,}

    def set_path_wms_openerp_purchase(self, cr, uid, ids, context=None):
        file = self.browse(cr, uid, ids[0], context)["path_wms_openerp_purchase"] or ""
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.path_wms_openerp_purchase", file)
        
    def get_default_wmsfiles_after_treated(self, cr, uid, fields, context=None):
        file = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.wmsfiles_after_treated") or ""
        return {'wmsfiles_after_treated': file,}

    def set_wmsfiles_after_treated(self, cr, uid, ids, context=None):
        file = self.browse(cr, uid, ids[0], context)["wmsfiles_after_treated"] or ""
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.wmsfiles_after_treated", file)
        
        
    def get_default_host(self, cr, uid, fields, context=None):
        host = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.host") or ""
        return {'host': host,}

    def set_host(self, cr, uid, ids, context=None):
        host = self.browse(cr, uid, ids[0], context)["host"] or ""
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.host", host)   
        
    def get_default_port(self, cr, uid, fields, context=None):
        port = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.port") or "22"
        return {'port': int(port),}

    def set_port(self, cr, uid, ids, context=None):
        port = self.browse(cr, uid, ids[0], context)["port"] or "22"
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.port", port)   

    def get_default_user(self, cr, uid, fields, context=None):
        user = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.user") or ""
        return {'user': user,}

    def set_user(self, cr, uid, ids, context=None):
        user = self.browse(cr, uid, ids[0], context)["user"] or ""
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.user", user)   

    def get_default_password(self, cr, uid, fields, context=None):
        password = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.password") or ""
        return {'password': password,}

    def set_password(self, cr, uid, ids, context=None):
        password = self.browse(cr, uid, ids[0], context)["password"] or ""
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.password", password)                       
   
    def get_default_db_name(self, cr, uid, fields, context=None):
        db_name = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.db_name") or "davidts_dev"
        return {'db_name': db_name,}

    def set_db_name(self, cr, uid, ids, context=None):
        db_name = self.browse(cr, uid, ids[0], context)["db_name"] or ""
        self.pool.get("ir.config_parameter").set_param(cr, uid, "davits.db_name", db_name)     
    
    #End Evolution #47021
order_configuration()

