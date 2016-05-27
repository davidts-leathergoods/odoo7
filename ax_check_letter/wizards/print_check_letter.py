# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _


class PrintCheckLetter(osv.osv_memory):
    _name = 'ax.print.check_letter'
    _description = _("Print check letter")

    def print_check_letter(self, cr, uid, ids, context=None):
        voucher_pool = self.pool.get('account.voucher')
        active_ids = context.get('active_ids', [])

        to_print_ids = []
        for voucher in voucher_pool.browse(cr, uid, active_ids, context=context):
            if voucher.ax_check_letter_batch_number and not voucher.ax_check_letter_printed:
                to_print_ids.append(voucher.id)

        voucher_pool.write(cr, uid, to_print_ids, dict(ax_check_letter_printed=True), context=context)

        if not to_print_ids:
            raise osv.except_osv(_("Check letter Error !"),
                                 _("No payment to edit. "
                                   "Please select payment with check letter to edit"))
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'check_letter',
            'name': 'check_letter',
            'context': context,
            'res_model': 'account.voucher',
            'datas': {
                'ids': to_print_ids,
                'model': 'account.voucher',
                'context': context,
            }}
