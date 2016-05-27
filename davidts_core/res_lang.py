#  begin Evolution #45137
from openerp.osv  import osv

class res_lang(osv.osv):
    _inherit = "res.lang"

    def create(self, cr, uid, vals, context={}):
        if vals['code'] == 'nl_NL' or 'de_DE' or 'it_IT' or 'es_ES':
            modobj = self.pool.get('ir.module.module')
            mids = modobj.search(cr, uid, [('state', '=', 'installed')])
            modobj.update_translations(cr, uid, mids, vals['code'], context or {})

res_lang()
#  end Evolution #45137
