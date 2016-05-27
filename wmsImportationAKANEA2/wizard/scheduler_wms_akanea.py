# -*- coding: utf-8 -*-
import os
import pysftp
import csv
from datetime import date

from openerp.osv import osv
from openerp.tools.translate import _

class scheduler_wms_akanea(osv.osv_memory):
    _name= 'scheduler.wms.akanea'
    _description ='Importation des fichiers de mouvements dans le systeme'

    def convertion_date (self,ladate):
	try:
	    d = date(int(ladate[0:4]),int(ladate[4:6]),int(ladate[6:8]))
	    return d
	except ValueError:
	    return None
	return None
	
    def execute_scheduler(self,cr,uid, context=None):
	path_archive_files = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.wmsfiles_after_treated")
	find_product = self.pool.get ("product.product")
	with pysftp.Connection(self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.host"), 
	    username=self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.user"), 
	    password=self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.password")) as sftp:
	    sftp.cwd(path_archive_files)
	    for file_mvtint in reversed(sftp.listdir()):
		if file_mvtint.find ("MVTINT") != -1:
		    with sftp.open (file_mvtint,'rb') as csv_file:
			wms_import = self.pool.get('wms.akanea.history.mvtint')
			data_mvt = csv.reader(csv_file,delimiter=';')
			for row in data_mvt:
			    produit = find_product.search(cr,uid,[('old_code','=',row[8])])
			    ref_id = None
			    if produit:
				#print produit[0]
				ref_id = produit[0]
			    item = {
				'code_stockeur':  row[0],
				'reference_transfert':  row[1],
				'libelle_transfert':  row[2],
				'n_cde_entree':  row[3],
				'date_reception':  self.convertion_date(row[4]),
				'type_mouvement_stock':  row[5],
				'code_mouvement_stock':  row[6],
				'code_depot':  row[7],
				'code_article':  row[8],
				'product_id': ref_id,
				'numero_lot':  row[9],
				'statut':  row[10],
				'disponibilite_stock':  row[11],
				'date_limite_vente':  self.convertion_date(row[12]),
				'douane':  row[13],
				'numero_palette':  row[14],
				'quantite_palettes_mouvementee':  row[15],
				'quantite_colis_mouvementee':  row[16],
				'quantite_uvc_mouvementee':  row[17],
				'poids_net':  row[18],
				'poids_brut':  row[19],
				'spcb':  row[20],
				'pcb':  row[21],
				'nombre_colis_couche':  row[22],
				'nombre_couche_palette':  row[23],
				'state': 'new',
			    }

			    wms_import.create (cr,uid,item,context=context)
		    if sftp.exists('MVTS_historique') is False:
			sftp.makedirs("MVTS_historique")
		    #move file to directory backup
		    sftp.get(file_mvtint,"/tmp/"+file_mvtint)
		    sftp.put("/tmp/"+file_mvtint,"MVTS_historique/"+file_mvtint,)
		    #remove tmp file
		    sftp.remove(file_mvtint)
		    os.remove ("/tmp/"+file_mvtint)
	    sftp.close()

	return True

    def button_action_scheduler_import_akanea (self,cr,uid,ids, context=None):
	return self.execute_scheduler(cr,uid)
    

scheduler_wms_akanea()