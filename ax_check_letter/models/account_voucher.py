# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.translate import _


class ax_account_voucher(osv.Model):
    _inherit = 'account.voucher'

    _columns = {
        'ax_check_letter_batch_number': fields.char(_("Check let. batch number"), size=128,
                                                    track_visibility='onchange'),
        'ax_check_letter_printed': fields.boolean(_("Check letter edited"),
                                                  track_visibility='onchange'),
        'ax_check_letter_template': fields.many2one('email.template', "Check letter template"),
        'ax_check_letter_recipient': fields.char(_("Check let. recipient"), size=80,
                                                 track_visibility='onchange',
                                                 help=_("Enter a name here that will replace the "
                                                        "customer (default check recipient)")),
    }

    def _get_default_ax_check_letter_template(self, cr, uid, context=None):
        model_data_obj = self.pool.get('ir.model.data')
        try:
            template_id = model_data_obj.get_object_reference(cr, uid, 'ax_check_letter', 'ax_check_letter_default_template')[1]
            return template_id or False
        except:
            return False

    _defaults = {
         'ax_check_letter_template': _get_default_ax_check_letter_template,
    }

    # CMo: Can someone explain me WTF is this for ?
    _track = {
        'ax_check_letter_batch_number': {},
        'ax_check_letter_printed': {},
    }

    def copy(self, cr, uid, id, default=None, context=None):
        default.update(dict(ax_check_letter_batch_number=None, ax_check_letter_printed=False))
        return super(ax_account_voucher, self).copy(cr, uid, id, default, context=context)