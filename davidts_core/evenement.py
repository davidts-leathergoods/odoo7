from openerp.osv import fields, osv
class evenement(osv.osv):
    _name = 'evenement.evenement'

    def _check_events(self, cr, uid, ids):
    #  TODO: check condition and return boolean accordingly
        event = self.browse(cr, uid, ids[0], context=None)
        if event.date_begin < event.date_end:
            return True

    _constraints = [(_check_events, 'Start date must be before End date ', []),]
    _columns = {
              'name': fields.char('name', size=20, required=True, readonly=False),
              'date_begin': fields.date('Start date'),
              'date_end': fields.date('End date'),
              'date_expedition': fields.date('Shipping date at the latest'),
              'type_evenement_id': fields.many2one('evenement.type', 'Type of event', required=False),
              'purchase_ids': fields.many2many('purchase.order', 'purchase_event_rel', 'event_id', 'purchase_id', 'Purchases'),
    }

evenement()
