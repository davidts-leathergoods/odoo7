# -*- coding: utf-8 -*-
import openerp
from openerp import netsvc, tools, pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
import psycopg2
import psycopg2.extras
import sys
import re
import csv
import codecs
import unicodedata

class bob50_exportation(osv.osv):
    _name = 'bob50.exportation'
    _order = 'date_exportation desc'
    _columns = {
	'date_exportation': fields.date('exportation', required=True),
	'date_debut': fields.date('date de debut',required=True),
	'date_fin': fields.date('date de fin',required=True),
	'user_id': fields.many2one('res.users','Responsible'),
    }
    _default = {
	'date_exportation': time.strftime('%Y-%m-%d'),
    }

    def check_sum_amounts(self, list_files):
	print list_files
	for diff_files in ['SAJ','SCNJ']:
	    csv_good_files= []
	    #trouve les fichiers associés
	    for type_files in ['ENT','LIGN']:
		for files in list_files:
		    if files.find(diff_files) != -1 and files.find(type_files) != -1:
			csv_good_files.append(files)
	    #lit le contenu des lignes en un tableau
	    contents_lign = list(csv.reader(open(csv_good_files[1]),delimiter=';'))
	    
	    with open (csv_good_files[0],'rb') as csv_ent:
		file_header = csv.reader(csv_ent,delimiter=';')
		for row in file_header:
		    indice_tableau = 0
		    while indice_tableau < len(contents_lign):
			if row[4] == contents_lign[indice_tableau][4]:
			    montant = float (contents_lign[indice_tableau][10].replace(',','.'))
			    tva = float (contents_lign[indice_tableau][14].replace(',','.'))
			    total = float (row[14].replace(',','.'))
			    #calcul spécial du à un soucis d'arrondi 
			    if abs(total - (montant+tva))  > 0.001 :
				if int (contents_lign[indice_tableau][5]) == 1:
				    contents_lign[indice_tableau][10] = str(montant + abs(total - (montant+tva))).replace(',','.')
				    contents_lign[indice_tableau][12] = str(montant + abs(total - (montant+tva))).replace(',','.')
			indice_tableau = indice_tableau + 1

	    corrected_file = csv.writer(open(csv_good_files[1],"w+"), delimiter=';')
	    for row in contents_lign:
		corrected_file.writerow(row)
	    
	    #remove all items on the list
	    del csv_good_files[:] 

    def generate_row (self,row,description):
	new_row = []
	for item in row:
	    new_row.append(item)

    def convert_unicode_to_utf8 (self,row,description):
	for i in range(len(row)):
	    if isinstance(row[i], unicode):
		row[i] = unicodedata.normalize('NFKD',row[i]).encode('ascii','ignore')
		if description[i] ==  "trem" or description[i] ==  "tremint" or description[i] ==  "tremext":
		    row[i] = re.compile("[\s\"]").sub(" ",row[i])
	return row

    _old_num_document = 0
    _number_line = 0

    def count_number_line (self,row,description):
	for i in range(len(row)):
	    if description[i] == "tdocno":
		if row[i] != self._old_num_document:
		    self._number_line= 1
		    self._old_num_document = row[i]
		else:
		    self._number_line= self._number_line +  1
		row[i+1] = self._number_line
	return row

    def execute_export (self,cr,uid,ids,*args):
	date_debut = ''
	date_fin = ''
	for export in self.browse(cr,uid,ids):
	    date_debut = export.date_debut
	    date_fin = export.date_fin

	bob50_conf = self.pool.get('bob50.configuration')
	list_files_to_check =[]
	for sql in bob50_conf.search(cr,uid,[]):
	    if bob50_conf.browse (cr,uid,sql).to_export == True:
		sql_query = bob50_conf.browse (cr,uid,sql).sql_request
		sql_query = sql_query.replace("#date_debut#",date_debut)
		sql_query = sql_query.replace("#date_fin#",date_fin)
		exportCSV = bob50_conf.browse (cr,uid,sql).directory_export+bob50_conf.browse (cr,uid,sql).file_name
		exportName = bob50_conf.browse (cr,uid,sql).directory_export+bob50_conf.browse (cr,uid,sql).name
		list_files_to_check.append(exportCSV)
		DSN = 'host=127.0.0.1 port=5432 dbname=davidts user=openerp password=2Z1yiHS§8Pw'

		column_names = []
		data_rows = []

		with psycopg2.connect (DSN) as connection:
		    with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
			cursor.execute(sql_query)
			column_names = [desc[0] for desc in cursor.description]
			with codecs.open(exportCSV,"w+",encoding='utf-8') as csvfile:
			    spamwriter = csv.writer(csvfile, delimiter=';')
			    for row in cursor:
				new_row = self.convert_unicode_to_utf8(list (row),column_names)
				if exportName.find('LIGN') != -1:
				    new_row = self.count_number_line (new_row,column_names);
				spamwriter.writerow(new_row)

	self.check_sum_amounts(list_files_to_check)
	return True

class bob50_header(osv.osv):
    _name = "bob50.exportation.header"


class bob50_configuration(osv.osv):
    _name = "bob50.configuration"
    _columns = {
	'name' : fields.char('Nom de la requete',200,required=True),
	'directory_export': fields.char('Repertoire d exportation',300, required=True),
	'sql_request': fields.text('Requete SQL a exporter en CSV'),
	'file_name': fields.char('Nom du fichier',50, required=True),
	'export_header': fields.boolean('Exporte l entete'),
	'to_export': fields.boolean('A exporter ?'),
    }

