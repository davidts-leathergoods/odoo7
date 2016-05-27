# -*- coding: utf-8 -*-

import openerp
from openerp import netsvc, tools, pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import datetime
import sys
import pysftp

class wms_akanea_internal_mvt(osv.osv):
    _name = 'wms.akanea.history.mvtint'
    _order = 'date_reception desc'
    _columns = {
    'code_stockeur': fields.char('Code stockeur', required=True),
    'reference_transfert': fields.char('Reference Transfert', required=False),
    'libelle_transfert': fields.char('Libelle Transfert', required=False),
    'n_cde_entree': fields.integer('N° Cde d entree', required=True),
    'date_reception': fields.date('Date de reception', required=True),
    'type_mouvement_stock': fields.char('Type du Mouvement de Stock', required=True),
    'code_mouvement_stock': fields.char('Code du mouvement de stock', required=True),
    'code_depot': fields.char('Code du Depôt ', required=True),
    'product_id': fields.many2one('product.product','Product',required=False),
    'code_article': fields.char('Code article', required=True),
    'numero_lot': fields.char('Numero de lot', required=False),
    'statut': fields.char('Statut', required=False),
    'disponibilite_stock': fields.char('Disponibilite de Stock', required=True),
    'date_limite_vente': fields.date('Date limite de vente ', required=False),
    'douane': fields.char('Douane', required=False),
    'numero_palette': fields.integer('Numero de palette', required=True),
    'quantite_palettes_mouvementee': fields.integer('Quantite palettes mouvementee', required=True),
    'quantite_colis_mouvementee': fields.integer('Quantite colis mouvementee', required=True),
    'quantite_uvc_mouvementee': fields.integer('Quantite UVC mouvementee', required=True),
    'poids_net': fields.float('Poids net', required=True),
    'poids_brut': fields.float('Poids brut', required=True),
    'spcb': fields.integer('SPCB', required=True),
    'pcb': fields.integer('PCB', required=True),
    'nombre_colis_couche': fields.integer('Nombre colis couche', required=True),
    'nombre_couche_palette': fields.integer('Nombre couche palette', required=True),
    'commentaire_import': fields.char('Remarque importation',required=False),
    'date_importation': fields.datetime('heure importation', required=False),
    'state': fields.selection([('new','Nouveau'),('dropped','Non importé'),('imported','Importé'),('imported_validated','Importé et validé'),('automatic_validation','Validation automatique')], 'Status', readonly=True),
    'stock_move_id' : fields.many2one('stock.move','Mouvement de stock',required=False),
    }

    def _execute_importation (self,cr,uid,ids,*args):
	move_obj = self.pool.get('stock.move')
	location_obj = self.pool.get('stock.location')
	id_inventory_lost = location_obj.search(cr,uid,[('complete_name','=','Virtual Locations / Inventory loss')])[0]
	id_stock = location_obj.search(cr,uid,[('complete_name','=','Emplacements physiques / Davidts / Stock')])[0]

	for importation in self.browse(cr,uid,[ids]):
	    if isinstance (importation['stock_move_id'], openerp.osv.orm.browse_record) :
		return  already_insert()
	    quant =  importation['quantite_uvc_mouvementee']
	    ref_prod = importation['product_id']
	    name = ''
	    id_moved = None
	    if ref_prod['name'] is not None:
		name = ref_prod['name']
	    if ref_prod.uom_id is None:
		return None
	    else:
		id_moved = move_obj.create (cr, uid, {
                'name': "INV:INV "+name,
	        'product_uom': ref_prod.uom_id.id,
	        'product_uos': ref_prod.uom_id.id,
                'product_id': ref_prod.id,
                'product_uos_qty': abs(quant),
                'product_qty': abs(quant),
                'tracking_id': False,
                'state': 'draft',
		'location_id': id_stock if quant <= 0 else id_inventory_lost,
		'location_dest_id': id_inventory_lost if quant <= 0 else id_stock,
        	}, context=None)

	return id_moved

    def execute_import_wms (self,cr,uid,ids,*args):
	for item_id in ids:
	    success = self._execute_importation (cr,uid,item_id,*args)
	    if success is not None:
		if not isinstance (success, already_insert):
		    self.write(cr,uid,[item_id],{'state':'imported','date_importation':datetime.datetime.now(),'stock_move_id':success,'commentaire_import':''})
	    else:
		self.write(cr,uid,[item_id],{'state':'dropped','date_importation':datetime.datetime.now(),'commentaire_import':'Article non trouvé'})
	return True


    def execute_import_wms_and_valide (self,cr,uid,ids,*args):
	for item_id in ids:
	    success = self._execute_importation (cr,uid,item_id,*args)
	    if success is not None:
		if not isinstance (success, already_insert):
		    move_obj = self.pool.get('stock.move')
		    move_obj.action_done (cr,uid,[success],context=None)
		    self.write(cr,uid,[item_id],{'state':'imported_validated','date_importation':datetime.datetime.now(),'stock_move_id':success,'commentaire_import':''})
	    else:
		self.write(cr,uid,[item_id],{'state':'dropped','date_importation':datetime.datetime.now(),'commentaire_import':'Article non trouvé'})
	return True


    def execute_import_wms_and_automatic_validated (self,cr,uid,ids,*args):
	for item_id in ids:
	    success = self._execute_importation (cr,uid,item_id,*args)
	    if success is not None:
		if not isinstance (success, already_insert):
		    move_obj = self.pool.get('stock.move')
		    move_obj.action_done (cr,uid,[success],context=None)
		    self.write(cr,uid,[item_id],{'state':'automatic_validation','date_importation':datetime.datetime.now(),'stock_move_id':success,'commentaire_import':''})
	    else:
		self.write(cr,uid,[item_id],{'state':'dropped','date_importation':datetime.datetime.now(),'commentaire_import':'Article non trouvé'})
	return True

class already_insert(object):
    _name = 'si existe deja'

class wms_akanea_mvt_config (osv.osv_memory):
    _name = 'automatic.import.akanea.config.settings'
    _inherit = 'sale.config.settings'
    _columns = {
	'automatic_import': fields.boolean('import automatique'),
    }

wms_akanea_mvt_config()