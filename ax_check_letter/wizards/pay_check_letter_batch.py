# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID


class AxPayCheckLetterBatch(osv.osv_memory):
    _name = 'ax.pay_check_letter_batch'
    _description = _("Pay check letter batch")

    _columns = {
        'check_number': fields.integer(_("Check number"), help=_("First check number"), required=True),
        'check_date': fields.date(_("Check Date"), required=True),
        'check_journal_id': fields.many2one('account.journal', _("Payment journal"), required=True),
    }

    _defaults = {
        'check_number': 1,
        'check_date': lambda self, cr, uid, c: fields.date.today(),
    }


    def pay_check_letter(self, cr, uid, ids, context=None):
        wizard_brws = self.browse(cr, uid, ids[0], context=context)
        active_ids = context['active_ids']

        sequence_obj = self.pool.get('ir.sequence')
        invoice_obj = self.pool.get('account.invoice')
        voucher_obj = self.pool.get('account.voucher')

        batch_sequence = sequence_obj.next_by_code(cr, uid, 'ax.check_letter.batch', context=context)
        check_number = wizard_brws.check_number

        voucher_ids = []
        for invoice_brws in invoice_obj.browse(cr, uid, active_ids, context=context):
            if invoice_brws.residual == 0. or not invoice_brws.ax_to_pay_check_letter:
                continue
            voucher_ids.append(
                invoice_obj.create_check_letter_voucher(cr, uid,
                                                        invoice_brws,
                                                        check_number,
                                                        wizard_brws.check_date,
                                                        wizard_brws.check_journal_id, context=context))
            check_number += 1

        voucher_obj.write(cr, uid, voucher_ids,
                          {'ax_check_letter_batch_number': batch_sequence,
                           'ax_check_letter_printed': False})
        return {'type': 'ir.actions.act_window_close'}
