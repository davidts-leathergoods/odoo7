# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.osv.osv import except_osv
import netsvc

class AxPayCheckLetterUnit(osv.osv_memory):
    _name = 'ax.pay_check_letter_unit'
    _description = _("Pay check letter unit")

    _columns = {
        'check_number': fields.integer(_("Check number"), help=_("First check number"), required=True),
        'recipient': fields.char(_("Recipient"), size=80,
                                 help=_("Enter a name here that will replace the "
                                        "customer (default check recipient)")),
    }

    _defaults = {
        'check_number': 1,
    }


    def pay_by_check_letter(self, cr, uid, ids, context=None):
        if context.get('active_model', None) != 'account.voucher' or len(context.get('active_ids',0))!=1:
            raise except_osv(_("Error"),_("Pay by check letter must be launched on Payment form"))

        wkf_service = netsvc.LocalService("workflow")

        sequence_obj = self.pool.get('ir.sequence')
        voucher_obj = self.pool.get('account.voucher')


        voucher_id = context['active_ids'][0]

        # We check that we are processing a reimbursement
        voucher_brws = voucher_obj.browse(cr, uid, voucher_id, context=context)
        if voucher_brws.type == 'receipt' and voucher_brws.amount > 0:
            raise except_osv(_("Error"),_("On reimbursment can be paid by check letter."
                                          " Amount must be < 0.0."))
        if voucher_brws.state != 'draft':
            raise except_osv(_("Error"),_("Check letter payment can be used only on vouchers in"
                                          "state 'Draft'"))

        wizard_brws = self.browse(cr, uid, ids[0], context=context)
        batch_sequence = sequence_obj.next_by_code(cr, uid, 'ax.check_letter.batch', context=context)

        voucher_update_values = {
            'ax_check_letter_batch_number': batch_sequence,
            'ax_check_letter_printed': False,
            'ax_check_letter_recipient': wizard_brws.recipient,
            'reference': wizard_brws.check_number,
        }
        voucher_obj.write(cr, uid, [voucher_id], voucher_update_values, context=context)
        wkf_service.trg_validate(uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
        return {'type': 'ir.actions.act_window_close'}
