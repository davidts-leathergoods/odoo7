# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.exceptions


class AudaxisMemoryAnalyzerSettings(osv.osv):

    _name = 'ax.memory_analyzer.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'dump_files_path': fields.char("Dump file directory", size=256, help="This path (absolute or relative) will be"
                                                                             "added before generated dump file name."
                                                                             "Relatives path are expressed from openerp root."
                                                                             "Eg. for buildout servers it's in parts/openerp..."),
        'debug_stats': fields.boolean('DEBUG_STATS', help="Print statistics during collection. This information can be useful when tuning the collection frequency."),
        'debug_collectable': fields.boolean('DEBUG_COLLECTABLE', help="Print information on collectable objects found."),
        'debug_uncollectable': fields.boolean('DEBUG_UNCOLLECTABLE', help="Print information of uncollectable objects found (objects which are not reachable but cannot be freed by the collector). These objects will be added to the garbage list."),
        'debug_instances': fields.boolean('DEBUG_INSTANCES', help="When DEBUG_COLLECTABLE or DEBUG_UNCOLLECTABLE is set, print information about instance objects found."),
        'debug_objects': fields.boolean('DEBUG_OBJECTS', help="When DEBUG_COLLECTABLE or DEBUG_UNCOLLECTABLE is set, print information about objects other than instance objects found."),
        'debug_saveall': fields.boolean('DEBUG_SAVEALL', help="When set, all unreachable objects found will be appended to garbage rather than being freed. This can be useful for debugging a leaking program."),
        'debug_leak': fields.boolean('DEBUG_LEAK', help="The debugging flags necessary for the collector to print information about a leaking program (equal to DEBUG_COLLECTABLE | DEBUG_UNCOLLECTABLE | DEBUG_INSTANCES | DEBUG_OBJECTS | DEBUG_SAVEALL)."),
    }

    def get_param(self, cr, uid, key, context=None):
        ir_config_parameter_obj = self.pool.get('ir.config_parameter')
        key = "ama.%s" % key
        value = ir_config_parameter_obj.get_param(cr, uid, key, context=context)
        return value

    def put_param(self, cr, uid, key, value, context=None):
        ir_config_parameter_obj = self.pool.get('ir.config_parameter')
        key = "ama.%s" % key
        ir_config_parameter_obj.set_param(cr, uid, key, str(value), context=context)
        return value

    def set_dump_files_path(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self.put_param(cr, uid, 'dump_files_path', record.dump_files_path, context=context)

    def get_default_dump_files_path(self, cr, uid, ids, context=None):
        value = self.get_param(cr, uid, 'dump_files_path', context=context)
        return {'dump_files_path': value}

    def set_debug_stats(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self.put_param(cr, uid, 'debug_stats', record.debug_stats, context=context)

    def get_default_debug_stats(self, cr, uid, ids, context=None):
        value = self.get_param(cr, uid, 'debug_stats', context=context)
        return {'debug_stats': eval(value)}

    def set_debug_collectable(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self.put_param(cr, uid, 'debug_collectable', record.debug_collectable, context=context)

    def get_default_debug_collectable(self, cr, uid, ids, context=None):
        value = self.get_param(cr, uid, 'debug_collectable', context=context)
        return {'debug_collectable': eval(value)}

    def set_debug_uncollectable(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self.put_param(cr, uid, 'debug_uncollectable', record.debug_uncollectable, context=context)

    def get_default_debug_uncollectable(self, cr, uid, ids, context=None):
        value = self.get_param(cr, uid, 'debug_uncollectable', context=context)
        return {'debug_uncollectable': eval(value)}

    def set_debug_instances(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self.put_param(cr, uid, 'debug_instances', record.debug_instances, context=context)

    def get_default_debug_instances(self, cr, uid, ids, context=None):
        value = self.get_param(cr, uid, 'debug_instances', context=context)
        return {'debug_instances': eval(value)}

    def set_debug_objects(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self.put_param(cr, uid, 'debug_objects', record.debug_objects, context=context)

    def get_default_debug_objects(self, cr, uid, ids, context=None):
        value = self.get_param(cr, uid, 'debug_objects', context=context)
        return {'debug_objects': eval(value)}

    def set_debug_saveall(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self.put_param(cr, uid, 'debug_saveall', record.debug_saveall, context=context)

    def get_default_debug_saveall(self, cr, uid, ids, context=None):
        value = self.get_param(cr, uid, 'debug_saveall', context=context)
        return {'debug_saveall': eval(value)}

    def set_debug_leak(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            self.put_param(cr, uid, 'debug_leak', record.debug_leak, context=context)

    def get_default_debug_leak(self, cr, uid, ids, context=None):
        value = self.get_param(cr, uid, 'debug_leak', context=context)
        return {'debug_leak': eval(value)}

