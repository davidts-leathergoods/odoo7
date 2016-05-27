# -*- coding: utf-8 -*-
##############################################################################
##
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import logging
import openerp

from openerp.osv import osv, fields

_logger = logging.getLogger("InoukMailCatcher")

_logger.info("started")

class IrMailServer(osv.osv):
    _name = "ir.mail_server"
    _inherit = _name

    def send_email(self, cr, uid, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False,
                   context=None):
        if not openerp.ik_sd_is_production_server:
            recipient = message['to']
            subject = message['subject']
            message.replace_header('to', openerp.ik_sd_email_debug_recipients)
            message.replace_header('subject', "IKMC_To:%s||%s" % (recipient, subject,))
            _logger.debug("Message '%s' for '%s' forwarded to '%s'", subject, recipient, openerp.ik_sd_email_debug_recipients)

        return super(IrMailServer, self).send_email(cr, uid, message, mail_server_id=mail_server_id, smtp_server=smtp_server,
                                                    smtp_port=smtp_port, smtp_user=smtp_user, smtp_password=smtp_password,
                                                    smtp_encryption=smtp_encryption, smtp_debug=smtp_debug, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
