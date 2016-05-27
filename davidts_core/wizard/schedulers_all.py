# -*- coding: utf-8 -*-

import os
from openerp.osv import osv
from openerp.tools.translate import _

class schedulers_wms_files(osv.osv_memory):
    _name = 'schedulers.wms.files'
    _description = 'Compute all schedulers'

    def execute_schedulers(self, cr, uid):
        PATH_JOB_SALE = '../../project_addons/openerp_wms/wms_openerp_sale/wms_openerp_sale/wms_openerp_sale_run.sh'
        path_files_sale = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.path_wms_openerp_sale")
        
        PATH_JOB_PURCHASE = '../../project_addons/openerp_wms/wms_openerp_purchase/wms_openerp_purchase/wms_openerp_purchase_run.sh'
        path_files_purchase = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.path_wms_openerp_purchase")
        
        path_archive_files = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.wmsfiles_after_treated")
        if  not path_files_sale or not path_archive_files:           
            raise osv.except_osv(_('Warning!'), _('Path non valide, please choose path from: (Settings => Sale => Davidts => Path: Read WMS sale files)'))
        else:
            os.system('sh ' +  PATH_JOB_SALE )
        if  not path_files_purchase or not path_archive_files:           
            raise osv.except_osv(_('Warning!'), _('Path non valide, please choose path from: (Settings => Sale => Davidts => Path: Read WMS purchase files)'))
        else:
            os.system('sh ' + PATH_JOB_PURCHASE )
        return  True
    
    def button_action_schudler_wms_files(self, cr, uid, ids, context=None):
        return self.execute_schedulers(cr, uid)

    def action_read_wms_files(self, cr, uid, context=None):
        return self.execute_schedulers(cr, uid) 

schedulers_wms_files()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
