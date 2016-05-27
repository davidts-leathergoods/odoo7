# -*- coding: utf-8 -*-
##############################################################################
#

##############################################################################

from openerp import tools
from openerp.osv import osv, fields
from datetime import datetime
import csv
import gc
import os


class AudaxisMemoryAnalyzer(osv.osv):
    """
    Expose the InoukMemoryAnalyzer object to the cron jobs mechanism.
    """
    _name = 'ax.memory_analyzer'

    _columns = {
    }

    @staticmethod
    def osv_memory_instances_count(cr, table_name):
        query = "SELECT COUNT(*) FROM %s;" % table_name
        cr.execute(query)
        sql_result = cr.fetchall()
        return sql_result[0][0]

    def stats_osv_memory(self, cr, uid, context=None):
        # TODO: log in CSV instead of print
        print "time,model_name,table_name,instances_count"
        for model in self.pool.models.values():
            if model.is_transient():
                nb_instances = self.osv_memory_instances_count(cr, model._table)
                if nb_instances:
                    print "%s,%s,%s,%s" % (datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT),
                                           model._name,
                                           model._table,
                                           nb_instances,)
        return True

    def compute_gc_flags_from_config(self, cr, uid):
        icp_obj = self.pool.get('ir.config_parameter')
        flags = 0
        if eval(icp_obj.get_param(cr, uid, 'ama.debug_stats')):
            flags = flags | gc.DEBUG_STATS
        if eval(icp_obj.get_param(cr, uid, 'ama.debug_collectable')):
            flags = flags | gc.DEBUG_COLLECTABLE
        if eval(icp_obj.get_param(cr, uid, 'ama.debug_uncollectable')):
            flags = flags | gc.DEBUG_UNCOLLECTABLE
        if eval(icp_obj.get_param(cr, uid, 'ama.debug_instances')):
            flags = flags | gc.DEBUG_INSTANCES
        if eval(icp_obj.get_param(cr, uid, 'ama.debug_objects')):
            flags = flags | gc.DEBUG_OBJECTS
        if eval(icp_obj.get_param(cr, uid, 'ama.debug_saveall')):
            flags = flags | gc.DEBUG_SAVEALL
        if eval(icp_obj.get_param(cr, uid, 'ama.debug_leak')):
            flags = flags | gc.DEBUG_LEAK
        return flags

    def compute_gc_dump_filename(self, cr, uid):
        """
        Computes the name of the dump file according to configuration parameters
        :param cr:
        :param uid:
        :param context:
        :return:
        """
        icp_obj = self.pool.get('ir.config_parameter')
        dump_path = icp_obj.get_param(cr, uid, 'ama.dump_files_path')
        file_name = "memory_analyzer_%s.csv" % datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(dump_path, file_name)

    # Bouton : dump all python object
    def stats_python_objects(self, cr, uid, ids=None, context=None):
        """
        This a cron job that dump memory usage according to parameters defined in configuration
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        """

        gc_flags = self.compute_gc_flags_from_config(cr, uid)
        gc.set_debug(gc_flags)

        csv.register_dialect('audaxis_memory_analyser', delimiter=',', quoting=csv.QUOTE_MINIMAL)
        with open(self.compute_gc_dump_filename(cr, uid), 'wb') as f:
            writer = csv.writer(f, 'audaxis_memory_analyser')
            writer.writerow("python_id,openerp,module_name,class_name,instance_name,len,additional_info".split(','))

            for e in gc.get_objects():
                class_name = e.__class__.__name__ if hasattr(e, '__class__') else None
                module_name = e.__class__.__module__ if class_name else None
                openerp_module = module_name.startswith('openerp') if module_name else False
                try:
                    len_info = len(e)
                except:
                    len_info = ''

                additional_info = ''
                instance_name = ''

                if class_name:
                    if openerp_module:
                        if class_name == 'Cursor':
                            if e._Cursor__closed:
                                class_name += ":Ccursor_Closed"
                                #instance_name = "Ccursor_Closed"
                            else:
                                class_name += ":%s" % (e._table_name if hasattr(e, '_table_name') else None,)
                                #instance_name = e._table_name if hasattr(e, '_table_name') else None
                                len_info = len(e._data) if hasattr(e, '_data') else None

                        elif class_name == 'browse_record_list':
                            class_name += ":%s" % e[0]._model._name
                            #instance_name = e[0]._model._name

                        elif class_name == "browse_record":
                            class_name += ":%s" % e._model._name
                            #instance_name = e._model._name

                        elif class_name == "Query":
                            additional_info = str(e).replace('"', '\'')
                            additional_info = additional_info.replace('|', '!')

                        elif class_name == "OpenERPSession":
                            class_name += ":login=%s" % e._login
                            #instance_name = e._login
                            additional_info = "db=%s" % e._db

                        elif class_name == "browse_null":
                            pass

                    else:  # Non OpenERP module
                        pass
                else:
                    pass

                line_content = "%s,%s,%s,%s,%s,%s,%s" % (id(e),
                                                         openerp_module,
                                                         module_name,
                                                         class_name,
                                                         instance_name,
                                                         len_info,
                                                         additional_info,)
                writer.writerow(line_content.split(','))

        return True

    def stats_python_garbage_objects(self, cr, uid, ids=None, context=None):
        """
        This a cron job that dump memory usage according to parameters defined in configuration
        :param cr:
        :param uid:
        :param ids:
        :param context:
        :return:
        """

        gc_flags = self.compute_gc_flags_from_config(cr, uid)
        gc.set_debug(gc_flags)

        if gc.garbage:
            csv.register_dialect('audaxis_memory_analyser', delimiter=',', quoting=csv.QUOTE_MINIMAL)
            with open(self.compute_gc_dump_filename(cr, uid), 'wb') as f:
                writer = csv.writer(f, 'audaxis_memory_analyser')
                writer.writerow("python_id,module_name,class_name,instance_name,size_info,additional_info".split(','))

                for e in gc.garbage:
                    if e.__class__.__module__.startswith('openerp'):
                        #print "%s,%s,%s" % (id(e), e.__class__.__module__, e.__class__.__name__,)

                        module_name = e.__class__.__module__
                        class_name = e.__class__.__name__

                        if class_name == 'Cursor':
                            if e._Cursor__closed:
                                instance_name = "Ccursor_Closed"
                                size_info = None
                            else:
                                instance_name = e._table_name
                                size_info = len(e._data)
                            additional_info = ''
                        elif class_name == 'browse_record_list':
                            instance_name = e[0]._model._name
                            size_info = len(e)
                            additional_info = ''
                        elif class_name == "browse_record":
                            instance_name = e._model._name
                            size_info = 1
                            other_data = ''
                        elif class_name == "Query":
                            instance_name = ''
                            size_info = ''
                            additional_info = str(e).replace('"', '\'')
                            additional_info = additional_info.replace('|', '!')
                            print additional_info
                        elif class_name == "OpenERPSession":
                            instance_name = e._login
                            size_info = ''
                            additional_info = "db=%s" % e._db
                        elif class_name == "browse_null":
                            instance_name = None
                            size_info = None
                            additional_info = None
                        else:
                            instance_name = None
                            size_info = None
                            additional_info = None

                        line_content = "%s,%s,%s,%s,%s,%s" % (id(e),
                                                              module_name,
                                                              class_name,
                                                              instance_name,
                                                              size_info,
                                                              additional_info,)
                        writer.writerow(line_content.split(','))

                        if e.__class__.__name__ not in ('Cursor', 'browse_record_list', 'browse_record', 'browse_null',
                                                        'OpenERPSession', 'Query'):
                            print "analyze: %s" % e
                            writer.writerow(",,,,,\"not analyzed:%s\"" % e)

        return True




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
