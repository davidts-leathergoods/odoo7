from openerp.osv import fields, osv

class DavidtsMetier(osv.osv):
    _name = 'davidts.metier'
    _columns = {
        'name': fields.char('Metier'),
    }

DavidtsMetier()

class inner_material(osv.osv):
    _name = 'davidts.inner_material'
    _columns = {
        'name': fields.char('Inner Material'),
    }
    
inner_material()

class outer_material(osv.osv):
    _name = 'davidts.outer_material'
    _columns = {
        'name': fields.char('Inner Material'),
    }
    
outer_material()

class DavidtsSub_Metier(osv.osv):
    _name = 'davidts.sub_metier'
    _columns = {
        'name': fields.char('Sub Metier'),
        'metier_id': fields.many2one('davidts.metier', 'Metier'),
    }

DavidtsSub_Metier()

class DavidtsGroupCharacteristic(osv.osv):
    _name = 'davidts.group_characteristic'
    _columns = {
        'name': fields.char('Characteristic'),
        'boolean_characteristic_id': fields.one2many('davidts.boolean_characteristic', 'characteristic_group_id',
                                                     'Boolean Characteristic'),
        'integer_characteristic_id': fields.one2many('davidts.integer_characteristic', 'characteristic_group_id',
                                                     'Integer Characteristic'),
        'text_characteristic_id': fields.one2many('davidts.text_characteristic', 'characteristic_group_id',
                                                  'Text Characteristic'),
        'selection_characteristic_id': fields.one2many('davidts.selection_characteristic', 'characteristic_group_id',
                                                       'Text Characteristic'),
    }

DavidtsGroupCharacteristic()

class DavidtsCharacteristic(osv.osv):
    _name = 'davidts.characteristic'
    _columns = {
        'name': fields.char('Characteristic'),
        'type': fields.selection([('integer', 'Integer'), ('boolean', 'Boolean'), ('text', 'Text'),
                                  ('selection', 'Selection')], 'Type'),
    }

DavidtsCharacteristic()

class DavidtsBooleanCharacteristic(osv.osv):
    _name = 'davidts.boolean_characteristic'
    _columns = {
        'characteristic_id': fields.many2one('davidts.characteristic', 'Boolean Characteristic', ondelete='set null',
                                             select=True),
        'value': fields.boolean('Value'),
        'characteristic_group_id': fields.many2one('davidts.group_characteristic', ondelete='cascade', select=True),
        'product_template_characteristic_group_id': fields.many2one('product.template',
                                                                    ondelete='cascade', select=True),
    }
    _rec_name = 'characteristic_id'

DavidtsBooleanCharacteristic()

class DavidtsIntegerCharacteristic(osv.osv):
    _name = 'davidts.integer_characteristic'
    _columns = {
        'characteristic_id': fields.many2one('davidts.characteristic', 'Integer Characteristic', ondelete='set null', select=True),
        'value': fields.integer('Value'),
        'characteristic_group_id': fields.many2one('davidts.group_characteristic', ondelete='cascade', select=True),
        'product_template_characteristic_group_id': fields.many2one('product.template', ondelete='cascade', select=True),
    }
    _rec_name = 'characteristic_id'

DavidtsIntegerCharacteristic()

class DavidtsTextCharacteristic(osv.osv):
    _name = 'davidts.text_characteristic'
    _columns = {
        'characteristic_id': fields.many2one('davidts.characteristic', 'Text Characteristic', ondelete='set null', select=True),
        'value': fields.char('Value', size=32),
        'characteristic_group_id': fields.many2one('davidts.group_characteristic', ondelete='cascade', select=True),
        'product_template_characteristic_group_id': fields.many2one('product.template', ondelete='cascade', select=True),
    }
    _rec_name = 'characteristic_id'

DavidtsIntegerCharacteristic()

class DavidtsSelectionCharacteristic(osv.osv):
    _name = 'davidts.selection_characteristic'
    _columns = {
        'characteristic_id': fields.many2one('davidts.characteristic', 'Selection Characteristic', ondelete='set null',
                                             select=True),
        'value_id': fields.many2one('davidts.selection_values', 'Values'),
        'characteristic_group_id': fields.many2one('davidts.group_characteristic', ondelete='cascade', select=True),
        'product_template_characteristic_group_id': fields.many2one('product.template', ondelete='cascade',
                                                                    select=True),
    }
    _rec_name = 'characteristic_id'

DavidtsSelectionCharacteristic()

class DavidtsSelectionValues(osv.osv):
    _name = 'davidts.selection_values'
    _columns = {
        'name': fields.char('Name', size=32),
    }
    
DavidtsSelectionValues()
