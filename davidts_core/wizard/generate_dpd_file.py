#! /usr/bin/env python
# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
from tempfile import TemporaryFile
import base64

class generate_dpd_file(osv.osv_memory):
    _name = 'generate.dpd.file'
    _description = 'Compute all schedulers'
    
    def default_get(self, cr, uid, fields, context):
        res = super(generate_dpd_file,self).default_get(cr, uid, fields, context)
        actives =context.get('active_ids',[]) 
        data = self.generate_file(cr, uid,actives, context)
        if 'dpd_data' in fields:
            res.update({'dpd_data': data['dpd_data']})
        if 'dpd_name_file' in fields:
            res.update({'dpd_name_file':data['dpd_name_file']})
        return res
    
    def generate_file(self,cr,uid,ids,context):
     tmpf = TemporaryFile('w+') 
     data = base64.encodestring(tmpf.read())
     for id_exp in ids:
           exp = self.pool.get('davidts.expedition').browse(cr, uid,id_exp,context = context)
           cl1 = 'NP'
           if exp.package_nb != 0:
               cl2 = str(exp.total_weight/exp.package_nb)
           else:  raise osv.except_osv(_('Attention'),
                                     _('Package quantity must be different of zero !!! ')) 
           cl10 = str(exp.package_nb)
           cl13 = exp.name
           if exp.expedition_adr.country.id :
               country_name = self.pool.get('res.country').browse(cr,uid,exp.expedition_adr.country.id,context).code
               cl21= str(country_name).encode('ascii','replace')
           else :   
               cl21 = ""
           if exp.expedition_adr.id :
               partner = self.pool.get('res.partner').browse(cr,uid,exp.expedition_adr.id,context)
               if partner.ref: 
                   cl14= partner.ref.encode('ascii','replace')
               else: 
                   cl14=""
               if partner.name: 
                   cl15= partner.name.encode('ascii','replace')
               else: 
                   cl15=""
               if partner.street: 
                   cl19= partner.street.encode('ascii','replace')
               else: 
                   cl19=""
               if partner.street2: 
                   cl20= partner.street2.encode('ascii','replace')
               else: 
                   cl20=""
               if partner.zip: 
                   cl22= partner.zip
               else: 
                   cl22=""
               if partner.city: 
                   cl23= partner.city.encode('ascii','replace')
               else: 
                   cl23=""
               if partner.city: 
                   cl24= partner.city.encode('ascii','replace')
               else: 
                   cl24=""
               if partner.phone: 
                   cl25= partner.phone
               else: 
                   cl25=""
               if partner.fax: 
                   cl26= partner.fax
               else: 
                   cl26=""
               if partner.email: 
                   cl27= partner.email.encode('ascii','replace')
               else: 
                   cl27=""
               line = cl1+";"+cl2+";;;;;;;;"+cl10+";;;"+cl13+";"+cl14+";"+cl15+";;;;"+cl19+";"+cl20+";"+cl21+";"+cl22+";"+cl23+";"+cl24+";"+cl25+";"+cl26+";"+cl27+";\n"
               file_name = "dpd.txt"
               for i in xrange(exp.package_nb):
                   tmpf.write(str(line))  
               tmpf.seek(0)
               data = base64.encodestring(tmpf.read())    
     return {'dpd_data':data,'dpd_name_file':"dpd.txt"}
 
    _columns = {
        'dpd_data': fields.binary('Fichier DPD', readonly=True),                
        'dpd_name_file': fields.char(string="Fichier DPD", required=False),
    }
    
    _defaults = {
    'dpd_name_file': "dpd.txt"
    }
    
generate_dpd_file()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
