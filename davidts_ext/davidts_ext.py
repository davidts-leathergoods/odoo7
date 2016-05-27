# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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


import openerp
from openerp.osv import fields, osv

class project_project(osv.osv):
    _inherit = 'project.project'

    def message_get_reply_to(self, cr, uid, ids, context=None):
        if not self._inherits.get('mail.alias') or self._name == 'project.project':
            return [False for id in ids]
        return ["%s@%s" % (record['alias_name'], record['alias_domain'])
                    if record.get('alias_domain') and record.get('alias_name')
                    else False
                    for record in self.read(cr, SUPERUSER_ID, ids, ['alias_name', 'alias_domain'], context=context)]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: