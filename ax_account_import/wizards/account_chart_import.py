# -*- coding: utf-8 -*- 

#import tarfile
#import tempfile
#import threading
#import codecs
#import fnmatch
#import inspect
#import itertools
#import re
#from lxml import etree

from tools.translate import _
 
from openerp import tools
import os
import sys
import xlrd
import time
import datetime
from openerp.osv import fields, osv
from openerp.osv.osv import except_osv
from unidecode import unidecode
import itertools
import logging
import base64
import encodings
_logger = logging.getLogger(__name__)

MAPPING_XL_VERS_POI = {

    "Account Code": {'field_name': 'code', 'field_type': 'string'},

    "Account Name": {'field_name': 'name', 'field_type': 'string'},

    "Parent Account": {'field_name': 'parent_id', 'field_type': 'string'},

    "Internal Type": {'field_name': 'type', 'field_type': 'string'},
 
    "Account Type": {'field_name': 'user_type', 'field_type': 'string'},
 
    "Active": {'field_name': 'active',  'field_type': 'string'},
 
    "Reconcile": {'field_name': 'reconcile',  'field_type': 'string'},
 
    "Note": {'field_name': 'note',  'field_type': 'text'},
 
 }

INDEX_FEUILLE_DONNEES = 0
INDEX_LIGNE_ENTETE = 0
INDEX_PREMIERE_LIGNE_DONNEES = INDEX_LIGNE_ENTETE + 1  # First line of data in XL files

class ImportChartAccountWizard(osv.osv_memory):
    _name = "import.account.wizard"
    _description = "Import chart account Wizard"

    _columns = {
               'inactivate_unused_accounts' : fields.boolean('Add Prefix Unused Accounts'),
               'file_data' : fields.binary('Import a XLS File', required=True),
               'uap' : fields.char('Unused account prefix', size=512 ),
                }
    
    _default = {
                'inactivate_unused_accounts': False,
                 }
     
    def import_file(self, cr, uid, ids, context=None):
    
                chart_account_obj = self.pool.get('account.account') 
                account_type_obj = self.pool.get('account.account.type') 
                res_partner_obj = self.pool.get('res.partner')
                model_data_obj = self.pool.get('ir.model.data')
                
                try:
                    wizard = self.browse(cr, uid, ids[0], context=context)
                    file = wizard.file_data
                    unused_accounts = wizard.inactivate_unused_accounts
                    new_name = "account_account"
                    wallet_path = self.save_file( cr, uid, new_name, file )
                    imported_account_list = list()
                except:
                    raise osv.except_osv(_('Warning'), _('Can not Import Chart Account file, Please try again'))
                parent_value_list = ['none' , '_none_', '__none__']
                type_lists = [ ('view' , 'Vue'),('other' , 'Normal'),('receivable' , 'compte client'),('payable' , 'fournisseur'),('liquidity' , 'liquidités'),('consolidation' , 'consolidation'),('closed' , 'fermé') ]    
                
                if wallet_path.endswith('.xls') or wallet_path.endswith('.xlsx'):
                    fichier_excel = xlrd.open_workbook(wallet_path)
                    fichier_excel.sheet_names()
                    sheet = fichier_excel.sheet_by_index(INDEX_FEUILLE_DONNEES)
                    # On charge la ligne d'entete
                    try:
                        ligne_entete =  sheet.row_values(INDEX_LIGNE_ENTETE) 
                        colonne_presentes_entete = [colonne.encode('utf8') for colonne in ligne_entete]
                    except:  
                        raise osv.except_osv(_('Warning'), _( 'Header can not be empty and can not have float or integer values' ))
        
                    _logger.debug("File contains %s rows" % sheet.nrows)
                    # On charge les lignes de données
                    for rownum in xrange(INDEX_PREMIERE_LIGNE_DONNEES, sheet.nrows):   #Number lignes of xls sheet
                        try: 
                            chart_account_values = {}
                            ligne_courante = sheet.row_values(rownum)
                            _logger.debug("Commence à traiter la ligne %s, %s" % (rownum, ligne_courante))
                            # on charge la ligne courante dans account_account
                            for index, valeur_cellule in enumerate(ligne_courante):
                                if valeur_cellule <> None:
                                    colonne_mappee = MAPPING_XL_VERS_POI.get(colonne_presentes_entete[index].strip(), None)
                                    if colonne_mappee:
                                        field_type = colonne_mappee['field_type']
                                        field_name = colonne_mappee['field_name']
                                        chart_account_values[field_name] = valeur_cellule
                                    else:
                                        raise osv.except_osv(_('Warning'), _( 'Header Line: Please verify header columns' ))
                        except:
                            raise osv.except_osv(_('Warning'), _( 'Header Line: Please verify header columns' ))
                        if chart_account_values.get('code'):
                            if type(chart_account_values['code']) in (float, int):
                                chart_account_values['code'] = str(int(chart_account_values['code'])).strip()
                            else:
                                chart_account_values['code'] = str((chart_account_values['code']).encode('utf-8')).strip()
                            account_ids = ()
                            if chart_account_obj.search(cr, uid, [('code', '=', chart_account_values['code'].strip())]):
                                account_ids = chart_account_obj.search(cr, uid, [('code', '=', chart_account_values['code'].strip())]) 
                                account_id = chart_account_obj.search(cr, uid, [('code', '=', chart_account_values['code'].strip())])[0]
                            elif chart_account_obj.search(cr, uid, [('code', '=', chart_account_values['code'].strip()),('active', '=', False)]):  
                                account_ids = chart_account_obj.search(cr, uid, [('code', '=', chart_account_values['code'].strip()),('active', '=', False)]) 
                                account_id = chart_account_obj.search(cr, uid, [('code', '=', chart_account_values['code'].strip()),('active', '=', False)])[0]
                             # Si la account existe, on l'update, sinon on la créé
                            if account_ids:
                                 account_dict_old = chart_account_obj.browse(cr, uid, account_id, context)
                                 try:
                                     str((chart_account_values['code'])).strip() != ''
                                 except:
                                     raise osv.except_osv(_('Warning'), _( 'Line %d: Account Code can not be NULL ' %  (rownum,) ))
                                 imported_account_list.append(str((chart_account_values['code'])).strip())
                                 del chart_account_values['code']
                                # On réalise les traitements Account
                                 if type(chart_account_values['name']) in (float, int):
                                    chart_account_values['name'] = str(int(chart_account_values['name'])).strip()
                                 else:
                                     chart_account_values['name'] = str((chart_account_values['name']).encode('utf-8')).strip()
                                 if (chart_account_values['name']).strip() == '':
                                    raise osv.except_osv(_('Warning'), _( 'Line %d: Account Name can not be empty ' %  (rownum,) ))
                                 # 1) parent_id reste le meme si le champ est à vide et se mettre à vide si le champ est à _NONE_
                                 if type(chart_account_values['parent_id']) not in (float, int):
                                    if (chart_account_values['parent_id'].strip()).lower() in parent_value_list:
                                        chart_account_values['parent_id'] = None
                                    elif chart_account_values['parent_id'].strip() == '':
                                         chart_account_values['parent_id'] = account_dict_old.parent_id.id
                                    else:
                                        raise osv.except_osv(_('Warning'), _( 'Line %d: Verify Parent Account Type' %  (rownum,) ))
                                 elif type(chart_account_values['parent_id']) in (float, int):
                                    account = chart_account_obj.search(cr, uid, [('id','=',chart_account_values['parent_id']) , ('type','=',"view")])
                                    if not account:
                                            raise osv.except_osv(_('Warning'), _( 'Line %d: Parent Account Type must be VIEW' %  (rownum,) ))
                                #type
                                 if (str(chart_account_values['type'])).strip() == '':
                                     chart_account_values['type'] = account_dict_old.type
                                 elif (str(chart_account_values['type'])).strip() != '':
                                     for type_list in type_lists:
                                         if ((str(chart_account_values['type'])).strip()).lower() in type_list:
                                             chart_account_values['type'] = type_list[0]
                                             break 
                                     else:
                                         raise osv.except_osv(_('Warning'), _( 'Line %d: Internal Type must be in: view | Vue ,other | Normal,receivable | Compte Client,payable | Fournisseur,liquidity | Liquidités,consolidation | Consolidation,closed | Fermé ' %  (rownum,) ))
                                 else:
                                     raise osv.except_osv(_('Warning'), _( 'Line %d: Internal Type must be in: view | Vue ,other | Normal,receivable | Compte Client,payable | Fournisseur,liquidity | Liquidités,consolidation | Consolidation,closed | Fermé ' %  (rownum,) ))
                                 #Account Type                                                            
                                 if type(chart_account_values['user_type']) not in (float, int):
                                    if (str(chart_account_values['user_type'])).strip() == '':
                                        chart_account_values['user_type'] = account_dict_old.user_type.id
                                    elif account_type_obj.search(cr, uid, [('name', '=', (str(chart_account_values['user_type'])).strip())]):
                                        account_type = account_type_obj.search(cr, uid, [('name', '=', (str(chart_account_values['user_type'])).strip())])[0]
                                        chart_account_values['user_type'] = account_type
                                    elif model_data_obj.search(cr, uid, [('name', '=', (str(chart_account_values['user_type'])).strip())]):
                                        model_id = model_data_obj.search(cr, uid, [('name', '=', (str(chart_account_values['user_type']).strip()))])[0]
                                        model = model_data_obj.browse(cr, uid, model_id, context=context)
                                        chart_account_values['user_type'] = model.res_id
                                    else: 
                                        raise osv.except_osv(_('Warning'), _( 'Line %d: Verify Account Type' %  (rownum,) ))
                                #field actif
                                 if type(chart_account_values['active']) in (float, int):
                                     chart_account_values['active'] = str(int(chart_account_values['active']))
                                 active = str(chart_account_values['active']).strip()
                                 vu = active.lower() 
                                 if vu in ["false","non","faux","n","f","0"]:
                                     chart_account_values['active'] = False
                                 elif vu in["vrai","oui","true","t","o","v","1"]:
                                     chart_account_values['active'] = True
                                 elif str(chart_account_values['active']).strip() == '':
                                     chart_account_values['active'] = account_dict_old.active
                                 else:
                                     raise osv.except_osv(_('Warning'), _( 'Line %d: Verify Active field' %  (rownum,) ))
                                #reconcile 
                                 chart_account_values['reconcile'] = True
                                 #Note 
                                 if type(chart_account_values['note']) in (float, int):
                                     chart_account_values['note'] = str(int(chart_account_values['note']))
                                 elif chart_account_values['note'].strip() == '':
                                     chart_account_values['note'] = account_dict_old.note
                                 # on récupère certaines valeurs avant update pour
                                 chart_account_obj.write(cr, uid, account_id, chart_account_values)
                            
                            else:
                                if type(chart_account_values['code']) in (float, int):
                                    chart_account_values['code'] = str(int(chart_account_values['code'])).strip()
                                if str((chart_account_values['code'])).strip() != '':
                                    chart_account_values['code'] = str(chart_account_values['code']).strip()
                                    code = str(chart_account_values['code']).strip()
                                else:
                                    raise osv.except_osv(_('Warning'), _( 'Line %d: Account Code can not be NULL ' %  (rownum,) ))
                                imported_account_list.append(str((chart_account_values['code'])).strip())
                                if type(chart_account_values['name']) in (float, int):
                                    chart_account_values['name'] = str(int(chart_account_values['name'])).strip()
                                else:
                                    chart_account_values['name'] = str((chart_account_values['name']).encode('utf-8')).strip()
                                if str((chart_account_values['name'])).strip() == '':
                                    raise osv.except_osv(_('Warning'), _( 'Line %d: Account Name can not be empty ' %  (rownum,) ))
                                if type(chart_account_values['parent_id']) in (float, int):
                                    account_id = chart_account_obj.search(cr, uid, [('id','=',chart_account_values['parent_id']) , ('type','=',"view")])
                                    if not account_id:
                                            raise osv.except_osv(_('Warning'), _( 'Line %d: Parent Account Type must be VIEW' %  (rownum,) ))
                                else:
                                    for i in range(1,len(code)):
                                        parent_code = chart_account_obj.search(cr, uid, [('code', '=', code[:len(code) - i]),('type','=',"view")])
                                        if parent_code:
                                            parent_code_id = chart_account_obj.search(cr, uid, [('code', '=', code[:len(code) - i]),('type','=',"view")])[0]
                                            account_dict_old = chart_account_obj.browse(cr, uid, parent_code_id, context)
                                            chart_account_values['parent_id'] = account_dict_old.id
                                            break
                                        else:
                                            chart_account_values['parent_id'] = None
                                #type
                                if (str(chart_account_values['type'])).strip() != '':
                                    for type_list in type_lists:
                                        if ((str(chart_account_values['type'])).strip()).lower() in type_list:
                                            chart_account_values['type'] = type_list[0]
                                            break 
                                    else:
                                        raise osv.except_osv(_('Warning'), _( 'Line %d: Internal Type must be in: view | Vue ,other | Normal,receivable | Compte Client,payable | Fournisseur,liquidity | Liquidités,consolidation | Consolidation,closed | Fermé ' %  (rownum,) ))
                                else:
                                    raise osv.except_osv(_('Warning'), _( 'Line %d: Internal Type can not be empty, must be in: view | Vue ,other | Normal,receivable | Compte Client,payable | Fournisseur,liquidity | Liquidités,consolidation | Consolidation,closed | Fermé ' %  (rownum,) ))
    
                                #Field Active
                                if type(chart_account_values['active']) in (float, int):
                                    chart_account_values['active'] = str(int(chart_account_values['active']))
                                active = str(chart_account_values['active']).strip()
                                vu = active.lower() 
                                if vu in ["false","non","faux","n","f","0"]:
                                    chart_account_values['active'] = False
                                elif vu in["vrai","oui", "true","t","o","v","1"]:
                                    chart_account_values['active'] = True
                                else:
                                   raise osv.except_osv(_('Warning'), _( 'Line %d: Verify Active field' %  (rownum,) ))
                                #reconcile 
                                chart_account_values['reconcile'] = True
                                 #Note
                                if type(chart_account_values['note']) in (float, int):
                                    chart_account_values['note'] = str(int(chart_account_values['note']))
                                #Account Type
                                if type(chart_account_values['user_type']) not in (float, int):
    #                                 if  (str(chart_account_values['user_type'])).strip()  == ''
    #                                     raise osv.except_osv(_('Warning'), _( 'Line %d: Verify Account Type' %  (rownum,) ))
                                    if (str(chart_account_values['user_type'])).strip() == '':
                                        raise osv.except_osv(_('Warning'), _( 'Line %d: Account Type can not be empty' %  (rownum,) ))
                                    elif account_type_obj.search(cr, uid, [('name', '=', (str(chart_account_values['user_type'])).strip())]):
                                        account_type = account_type_obj.search(cr, uid, [('name', '=', str(chart_account_values['user_type']).strip())])[0]
                                        chart_account_values['user_type'] = account_type
                                    elif model_data_obj.search(cr, uid, [('name', '=', str(chart_account_values['user_type']).strip())]):
                                        model_id = model_data_obj.search(cr, uid, [('name', '=', str(chart_account_values['user_type']).strip())])[0]
                                        model = model_data_obj.browse(cr, uid, model_id, context=context)
                                        chart_account_values['user_type'] = model.res_id 
                                    else: 
                                        raise osv.except_osv(_('Warning'), _( 'Line %d: Verify Account Type' %  (rownum,) ))
                                chart_account_obj.create(cr, uid, chart_account_values)
        #                        assert account_id, "Unable to create Account."
                        else:
                            raise osv.except_osv(_('Warning'), _('Can not import chart of account. Please verify your file.'))
                    if wizard.inactivate_unused_accounts == True:
                        account_inactive_ids = chart_account_obj.search(cr, uid, [('type', 'not like' , 'view' ) , ('code' , 'not in' , imported_account_list), ('unused_accounts_prefixe' , '=' , False)])
                        if account_inactive_ids:
                            for account_inactive_id in account_inactive_ids:
                                account_dict_inactive = chart_account_obj.browse(cr, uid, account_inactive_id, context)
                                value = 'account.account,' + str(account_inactive_id)
                                partner_prop_acc = self.pool.get('ir.property').search(cr, uid, [('value_reference','=',value)], context=context)
                                if partner_prop_acc:
                                    chart_account_obj.write(cr, uid, account_inactive_id , {'code' : (wizard.uap + " - " + account_dict_inactive.code), 'unused_accounts_prefixe' : True })
                                else:
                                    chart_account_obj.write(cr, uid, account_inactive_id , {'code' : (wizard.uap + " - " + account_dict_inactive.code), 'unused_accounts_prefixe' : True , 'active' : False})
                    os.remove(wallet_path)
                else: 
                    raise osv.except_osv(_('Warning'), _('Can not Import Chart Account file => File extension is not .xls or .xlsx'))
          
          
    def save_file(self, cr, uid, name, value):
        date = time.strftime('%d-%m-%Y', time.localtime())
        current_directory = os.getcwd()
        path = "/%s/%s%s.xls" % (current_directory, name, date)
        try:
            f = open(path, 'wb+')
            f.write(base64.decodestring(value))
            f.close()
        except Exception as e:
            raise except_osv("Erreur ecriture Portefeuille", "Impossible d'enregistrer le fichier." % (path))
        return path
