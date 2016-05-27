from openerp.osv import fields, osv

class type_evenement(osv.osv):
    _name = 'evenement.type'
    _columns = {'name': fields.char('name', size=20, required=True, readonly=False),
              'evenement_ids': fields.one2many('evenement.evenement', 'type_evenement_id', 'Events', required=False),
              }

type_evenement()
