# -*- coding: utf-8 -*-
import os
import pysftp
import csv
from datetime import date

from openerp.osv import osv
from openerp.tools.translate import _

class multi_import_stock_mvt_wizard (osv.osv_memory):
    _name= 'multi.import.wms.akanea'
    _description ='Importation des fichiers de mouvements dans le systeme'

    def convertion_date (self,ladate):
	try:
	    d = date(int(ladate[0:4]),int(ladate[4:6]),int(ladate[6:8]))
	    return d
	except ValueError:
	    return None
	return None

    def multi_imports (self,cr,uid,ids,context=None):
	if context is None:
	    context = {}
	import_stock_obj = self.pool.get('wms.akanea.history.mvtint')
	import_stock_obj.execute_import_wms (cr,uid,context.get('active_ids',[]),context)
	return True

    def multi_imports_valide (self,cr,uid,ids,context=None):
	if context is None:
	    context = {}
	import_stock_obj = self.pool.get('wms.akanea.history.mvtint')
	import_stock_obj.execute_import_wms_and_valide (cr,uid,context.get('active_ids',[]),context)
	return True


multi_import_stock_mvt_wizard()