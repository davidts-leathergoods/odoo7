# -*- coding: utf-8 -*-
##############################################################################
#
#    jasper_server module for OpenERP, Management module for Jasper Server
#    Copyright (C) 2011 SYLEAM (<http://www.syleam.fr/>)
#              Christophe CHAUVET <christophe.chauvet@syleam.fr>
#
#    This file is a part of jasper_server
#
#    jasper_server is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    jasper_server is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
_logger = logging.getLogger('jasper_server')
import os
from openerp import netsvc
from openerp.osv import osv
from openerp.report.report_sxw import report_sxw, report_rml
from openerp.tools.translate import _

class IrActionReport(osv.osv):
    _inherit = 'ir.actions.report.xml'

    def register_all(self, cursor):
        """
        Register all jasper report
        """
        res = super(IrActionReport, self).register_all(cursor)
       
        opj = os.path.join
        cursor.execute("SELECT * FROM ir_act_report_xml WHERE auto=%s ORDER BY id", (True,))
        result = cursor.dictfetchall()
        print "register_all" +str(result)
        svcs = netsvc.Service._services
        for r in result:
            if svcs.has_key('report.'+r['report_name']):
                continue
            if r['report_rml'] or r['report_rml_content_data']:
                report_sxw('report.'+r['report_name'], r['model'],
                        opj('addons',r['report_rml'] or '/'), header=r['header'])
            elif r['report_xsl'] and r['report_xml']:
                report_rml('report.'+r['report_name'], r['model'],
                        opj('addons',r['report_xml']),
                        r['report_xsl'] and opj('addons',r['report_xsl']))
                
        return res


                
IrActionReport()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
