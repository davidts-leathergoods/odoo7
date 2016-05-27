# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _

import time


class base_module_data(osv.osv_memory):
    _name = 'base.module.data'
    _description = "Base Module Data"

    _columns = {
        'check_date': fields.datetime('Record from Date'),
        'objects': fields.many2many('ir.model', 'base_module_record_model_rel', 'objects', 'model_id', 'Objects'),
        'object_id': fields.many2one('ir.model', "Exported object", required=True),
        'preferred_module_name': fields.char("Preferred module name", size=64, help="Preferred module name used for external id resolution."),
        'exported_columns_ids': fields.many2many('ir.model.fields', help="List of exported columns. If empty will export all columns"),
        'excluded_columns_names': fields.char("CSV list of column names to exclude", size=512, help="Columns that will never be exported (even if specified above"),
        'filter_cond': fields.selection([('created', 'Created'), ('modified', 'Modified'), ('created_modified', 'Created & Modified')], 'Records only', required=True),
        'info_yaml': fields.boolean('YAML'),
    }

    _defaults = {
        # 'check_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'filter_cond': 'created_modified',
        'exported_columns_ids': None,
        'excluded_columns_names': None,
    }
    
    def _create_xml(self, cr, uid, context=None, exported_columns_name={}, excluded_columns_name={}):
        mod = self.pool.get('ir.module.record')
        res_xml = mod.generate_xml(cr, uid, exported_columns_name=exported_columns_name, excluded_columns_name=excluded_columns_name)
        return {'res_text': res_xml}

    def record_objects(self, cr, uid, ids, context=None):
        wizard_dict = self.browse(cr, uid, ids[0], context=context)

        ir_module_record_obj = self.pool.get('ir.module.record')
        ir_model_obj = self.pool.get('ir.model')
        ir_model_data_obj = self.pool.get('ir.model.data')

        ir_module_record_obj.recording_data = []

        object_name = wizard_dict.object_id.model

        searched_obj = self.pool.get(object_name)

        # we search records to export in search_ids
        search_condition = []
        if wizard_dict.check_date:
            if filter == 'created':
                search_condition = [('create_date', '>', check_date)]
            elif filter == 'modified':
                search_condition = [('write_date', '>', check_date)]
            elif filter == 'created_modified':
                search_condition = ['|', ('create_date', '>', check_date), ('write_date', '>', check_date)]

        # we skip objects with _auto = False
        # we remove objects with_log_access = False from search
        # TODO: double check this as I don't understand it
        #if '_log_access' in dir(searched_obj):
        #    if not searched_obj._log_access:
        #        search_condition = []
        #    if '_auto' in dir(searched_obj):
        #        if not searched_obj._auto:
        #            continue

        # we retreive the list of ids to export and store it
        # in ir_module_record_obj.recording_data.
        search_ids = searched_obj.search(cr, uid, search_condition)
        for s_id in search_ids:
            args = (cr.dbname, uid, object_name, 'copy', s_id, {}, context)
            ir_module_record_obj.recording_data.append(('query', args, {}, s_id))

        # we create a dict with the list of column to export. Empty dict means export all
        # we use a dict (not a list) because of future plans
        exported_columns_names = {}
        if wizard_dict.exported_columns_ids:
            exported_columns_names = {column.name: True for column in wizard_dict.exported_columns_ids}

        excluded_columns_names = []
        if wizard_dict.excluded_columns_names:
            excluded_columns_names = wizard_dict.excluded_columns_names.split(',')

        # generate content
        if len(ir_module_record_obj.recording_data):
            res = self._create_xml(cr, uid, context=context, exported_columns_name=exported_columns_names, excluded_columns_name=excluded_columns_names)

        # return the result view
        if len(ir_module_record_obj.recording_data):
            view_ids = ir_model_data_obj.search(cr, uid, [('model', '=', 'ir.ui.view'), ('name', '=', 'module_create_xml_view')], context=context)
            resource_id = ir_model_data_obj.read(cr, uid, view_ids, fields=['res_id'], context=context)[0]['res_id']
            return {
                'name': _('Data Recording'),
                'context': {'default_res_text': tools.ustr(res['res_text'])},
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'base.module.record.data',
                'views': [(resource_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

        view_ids = ir_model_data_obj.search(cr, uid, [('model', '=', 'ir.ui.view'), ('name', '=', 'module_recording_message_view')], context=context)
        resource_id = ir_model_data_obj.read(cr, uid, view_ids, fields=['res_id'], context=context)[0]['res_id']
        return {
            'name': _('Module Recording'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'base.module.record.objects',
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

base_module_data()

class base_module_record_data(osv.osv_memory):
    _name = 'base.module.record.data'
    _description = "Base Module Record Data"
                
    _columns = {
        'res_text': fields.text('Result'),
    }    
    
base_module_record_data()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
