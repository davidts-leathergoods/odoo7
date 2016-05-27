from openerp.osv import osv, fields
from openerp.tools.translate import _
import netsvc


class ax_account_invoice(osv.Model):
    _inherit = 'account.invoice'

    _columns = {
        'ax_to_pay_check_letter': fields.boolean(_("To pay with check-letter"), track_visibility='onchange'),
    }

    _defaults = dict(ax_to_pay_check_letter=False)

    _track = {
        'ax_to_pay_check_letter': {
        },
    }

    def copy(self, cr, uid, id, default=None, context=None):
        default.update(dict(ax_to_pay_check_letter=False))
        return super(ax_account_invoice, self).copy(cr, uid, id, default, context=context)

    def set_ax_to_pay_check_letter(self, cr, uid, ids, context=None):
        """ Set refund to be pay with check letter."""
        reads = self.read(cr, uid, ids, ['ax_to_pay_check_letter', 'residual', 'type', 'number', 'state'], context=context)
        for acc_inv_r in reads:
            if acc_inv_r['state'] != 'open':
                raise osv.except_osv(_("Check letter error !"), _("Selected refund is not in state 'open'"))
            elif acc_inv_r['ax_to_pay_check_letter']:
                raise osv.except_osv(_("Check letter error !"), _("Refund %s is already marqued as to pay with check letter" % acc_inv_r['number']))
            elif acc_inv_r['residual'] == 0.:
                raise osv.except_osv(_("Check letter error !"), _("Refund %s have no residual amount to pay" % acc_inv_r['number']))
            elif acc_inv_r['type'] != 'out_refund':
                raise osv.except_osv(_("Check letter error !"), _("Invoice %s is not a customer refund" % acc_inv_r['number']))

            self.write(cr, uid, acc_inv_r['id'],
                       {'ax_to_pay_check_letter': True}, context=context)

    def create_check_letter_voucher(
            self, cr, uid, refund_brw, sequence_num, check_date, journal_brw, context=None):
        account_voucher_obj = self.pool.get('account.voucher')
        wf_service = netsvc.LocalService("workflow")
        if refund_brw.type != 'out_refund':
            raise osv.except_osv(_("Internal error !"),
                                 _("invoice %s marqued to be pay with check "
                                   "letter was not a refund invoice !" % refund_brw.number))
        period = self.pool.get('account.period')
        period_id = period.find(cr, uid, check_date, context=context)[0]
        account_move_brw = refund_brw.move_id
        move_line_brw = [acc_ml for acc_ml in account_move_brw.line_id
                         if acc_ml.account_id.type == 'receivable'][0]
        
        partner_id = self.pool.get('res.partner')._find_accounting_partner(refund_brw.partner_id).id
        residual = refund_brw.residual
        amount = refund_brw.amount_total
        
        if amount == 0.:
            return False
        currency_id = refund_brw.currency_id.id
        val_voucher = {
            'period_id': period_id,
            'journal_id': journal_brw.id,
            'account_id': journal_brw.default_credit_account_id.id,
            'reference': str(sequence_num),
            'amount': -residual,
            'comment': '',
            'is_multi_currency': False,
            'date': check_date,
            'line_cr_ids': [],
            'line_dr_ids': [[0,
                             False,
                             {'account_id': move_line_brw.account_id.id,
                              'amount': residual,
                              'amount_original': amount,
                              'amount_unreconciled': residual,
                              'currency_id': currency_id,
                              'date_due': check_date,
                              'date_original': check_date,
                              'move_line_id': move_line_brw.id,
                              'reconcile': True,
                              'type': 'dr'}]],
            'name': refund_brw.number,
            'narration': False,
            'partner_id': partner_id,
            'payment_option': 'without_writeoff',
            'type': 'receipt',
            'pre_line': True,
            'comment': 'write-off',
            'writeoff_acc_id': False}
        context = {
            'type': 'receipt',
        }
        voucher_id = account_voucher_obj.create(cr, uid, val_voucher, context=context)
        wf_service.trg_validate(
            uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
        return voucher_id

