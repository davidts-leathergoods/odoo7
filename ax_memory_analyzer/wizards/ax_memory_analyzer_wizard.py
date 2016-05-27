# -*- coding: utf-8 -*-
##############################################################################
#

##############################################################################

from openerp import tools
from openerp.osv import osv, fields
from datetime import datetime
import gc


class AudaxisMemoryAnalyzerWizard(osv.osv_memory):
    """
    Expose the AudaxisMemoryAnalyzer object to the cron jobs mechanism.
    """
    _name = 'ax.memory_analyzer_wizard'

    _columns = {}

    def stats_python_objects(self, cr, uid, ids=None, context=None):

        ama_obj = self.pool.get('ax.memory_analyzer')
        return ama_obj.stats_python_objects(cr, uid, context=context)

    def stats_python_garbage_objects(self, cr, uid, ids=None, context=None):

        ama_obj = self.pool.get('ax.memory_analyzer')
        return ama_obj.stats_python_garbage_objects(cr, uid, context=context)

    def stats_osv_memory(self, cr, uid, ids=None, context=None):
        ama_obj = self.pool.get('ax.memory_analyzer')
        return ama_obj.stats_osv_memory(cr, uid, context=context)




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
