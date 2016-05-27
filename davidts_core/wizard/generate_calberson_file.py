from openerp.osv import fields, osv
from tempfile import TemporaryFile
import base64

class generate_calberson_file(osv.osv_memory):
    _name = 'generate.calberson.file'
    _description = 'generate calberson file'
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(generate_calberson_file,self).default_get(cr, uid, fields, context)
        actives =context.get('active_ids',[]) 
        data = self.generate_calberson_file(cr, uid,actives, context)
        if 'calberson_data' in fields:
            res.update({'calberson_data': data['calberson_data']})
        if 'calberson_name_file' in fields:
            res.update({'calberson_name_file':data['calberson_name_file']})
        return res
       
    def generate_calberson_file(self, cr, uid, ids, context=None):
        tmpf = TemporaryFile('w+') 
        data = base64.encodestring(tmpf.read())
        for id_exp in ids:
            exp = self.pool.get('davidts.expedition').browse(cr, uid, id_exp, context=context)
            if exp.expedition_adr.country.id:
                code_country = self.pool.get('res.country').browse(cr, uid, exp.expedition_adr.country.id, context).code 
            else:   
                code_country = False
            
            cl1 = '8796522'
            cl8 =   self.adapt(cr, uid, ids, exp.name, 9, context)     
            cl17 = ""
            for i in range(21):
                cl17 = cl17 + " " 
            cl38 =   self.adapt(cr, uid, ids, exp.expedition_adr.name, 35, context)  
            c73 = ""   
            for i in range(35):
                c73 = c73 + " "            
            cl108 = self.adapt(cr, uid, ids, exp.expedition_adr.street, 35, context) 
            c143 = ""
            for i in range(10):
                c143 = c143 + " "  
                
            cl153 = self.adapt(cr, uid, ids, code_country, 2, context)     
            cl155 = self.adapt(cr, uid, ids, exp.expedition_adr.zip, 5, context)  
            c160 = ""   
            for i in range(5):
                c160 = c160 + " "             
            cl165 = self.adapt(cr, uid, ids, exp.expedition_adr.city, 35, context) 
            c200 = "" 
            for i in range(85):
                c200 = c200 + " "             
            cl285 = self.adapt(cr, uid, ids, exp.package_nb, 3, context)     
            cl288 = self.adapt(cr, uid, ids, exp.palette_nb, 3, context)     
            cl291 = self.adapt(cr, uid, ids, exp.total_weight, 5, context) 
            c296 = ""
            for i in range(231):
                c296 = c296 + " "     
            cl528 = self.adapt(cr, uid, ids, exp.note, 35, context) 

            line = cl1+cl8+cl17+cl38+c73+cl108+c143+cl153+cl155+c160+cl165+c200+cl285+cl288+cl288+cl291+c296+cl528
            file_name = "calberson.anc"            
            tmpf.write(str(line))  
            tmpf.seek(0)
            data = base64.encodestring(tmpf.read())
            
        return {'calberson_data':data,'calberson_name_file':"calberson.anc"}
   
    _columns = {
        'calberson_data': fields.binary('Fichier Calberson',readonly=True), 
        'calberson_name_file':fields.char('Fichier Calberson',required=False),
    }
    
    _defaults = {
        'calberson_name_file':"calberson.anc"
    }
    
    def adapt(self, cr, uid, ids, column, length, context=None):
        cl2str = str(column)
        if column == False:
            cl2str = ""
            for i in range(length):
                cl2str = cl2str + " "   
        else:             
            if (cl2str.__len__() != length):
                diff = length - cl2str.__len__()
                if diff > 0:
                    for i in range(diff):
                        cl2str = cl2str + " "
                else:
                    cl2str = cl2str[:length]
        return   cl2str      
    
generate_calberson_file()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
