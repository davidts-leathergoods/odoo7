# -*- coding: utf-8 -*-
from anybox.testing.openerp import TransactionCase
from datetime import datetime, timedelta
from openerp.osv import fields, osv
import netsvc


class TestCheckLetter(TransactionCase):

    def setUp(self):
        super(TestCheckLetter, self).setUp()
        self.invoice = self.registry('account.invoice')
        self.voucher = self.registry('account.voucher')
        self.wf_service = netsvc.LocalService("workflow")
        self.partner_example_00 = self.ref('base.res_partner_2')
        self.journal_id = self.ref('account.check_journal')
        self.journal = self.registry('account.journal')

    def create_credit_note(self, partner_id, amount, confirm=True):
        cr, uid = self.cr, self.uid
        vals_credit_note = {
            'partner_id': partner_id,
            'account_id': self.ref('account.a_recv'),
            'comment': False,
            'company_id': self.ref('base.main_company'),
            'currency_id': self.ref('base.EUR'),
            'date_due': False,
            'date_invoice': False,
            'fiscal_position': False,
            'invoice_line': [[
                0,
                False,
                {'account_analytic_id': False,
                 'account_id': self.ref('account.a_sale'),
                 'discount': 0,
                 'invoice_line_tax_id': [[6, False, []]],
                 'name': '[ADPT] USB Adapter',
                 'price_unit': amount,
                 'product_id': self.ref('product.product_product_48'),
                 'quantity': 1,
                 'uos_id': self.ref('product.product_uom_unit')
                 }]],
            'journal_id': self.ref('account.refund_sales_journal'),
        }
        ctx = {
            'default_type': 'out_refund',
            'journal_type': 'sale_refund',
            'type': 'out_refund',
        }
        invoice_id = self.invoice.create(cr, uid, vals_credit_note, context=ctx)
        self.invoice.button_compute(cr, uid, [invoice_id])
        if confirm:
            self.wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
        return invoice_id

    def pay_credit_note(self, partner_id, refund_id, amount):
        refund_brw = self.invoice.browse(self.cr, self.uid, refund_id)
        account_move_brw = refund_brw.move_id
        move_line_id = [acc_ml.id for acc_ml in account_move_brw.line_id
                        if acc_ml.account_id.type == 'receivable'][0]
        date = fields.date.today()
        val_voucher = {'account_id': self.ref('account.cash'),
                       'amount': -amount,
                       'comment': '',
                       'is_multi_currency': False,
                       'date': date,
                       'journal_id': self.ref('account.check_journal'),
                       'line_cr_ids': [],
                       'line_dr_ids': [[0,
                                        False,
                                        {'account_id': self.ref('account.a_recv'),
                                         'amount': amount,
                                         'amount_original': amount,
                                         'amount_unreconciled': amount,
                                         'currency_id': self.ref('base.EUR'),
                                         'date_due': date,
                                         'date_original': date,
                                         'move_line_id': move_line_id,
                                         'name': 'test_paid_refund',
                                         'reconcile': True,
                                         'type': 'dr'}]],
                       'name': False,
                       'narration': False,
                       'partner_id': partner_id,
                       'payment_option': 'without_writeoff',
                       # 'payment_rate': 1,
                       'payment_rate_currency_id': self.ref('base.EUR'),
                       'period_id': self.ref('account.period_2'),
                       # 'pre_line': 1,
                       'reference': False,
                       'type': 'receipt',
                       'writeoff_acc_id': False}
        context = {'lang': 'en_US',
                   'type': 'receipt',
                   'tz': 'Europe/Brussels',
                   'uid': self.uid}
        voucher_id = self.voucher.create(self.cr, self.uid, val_voucher, context=context)
        self.wf_service.trg_validate(
            self.uid, 'account.voucher', voucher_id, 'proforma_voucher', self.cr)
        return voucher_id

    def test_set_refund_to_pay(self):
        """ Simulate a click on refund button to pay with check letter.
        """
        cr, uid = self.cr, self.uid
        refund_id = self.create_credit_note(self.partner_example_00, 20.)
        self.assertRecord(self.invoice, refund_id, dict(ax_to_pay_check_letter=False))
        self.invoice.set_ax_to_pay_check_letter(cr, uid, [refund_id])
        self.assertRecord(self.invoice, refund_id, dict(ax_to_pay_check_letter=True))

    def test_set_refund_to_pay_when_no_residual(self):
        """ ax_to_pay_check_letter flag must not be set because the invoice is totally payed.
        """
        cr, uid = self.cr, self.uid
        refund_id = self.create_credit_note(self.partner_example_00, 20.)
        self.pay_credit_note(self.partner_example_00, refund_id, 20.)
        try:
            self.invoice.set_ax_to_pay_check_letter(cr, uid, [refund_id])
            self.fail()
        except osv.except_osv:
            pass

    def test_set_refund_to_pay_when_no_confirm(self):
        """ ax_to_pay_check_letter flag must not be set because the invoice is not confirmed.
        """
        cr, uid = self.cr, self.uid
        refund_id = self.create_credit_note(self.partner_example_00, 20., confirm=False)
        try:
            self.invoice.set_ax_to_pay_check_letter(cr, uid, [refund_id])
            self.fail()
        except osv.except_osv:
            pass

    def test_can_pay_credit_note_with_voucher(self):
        """ We use a custom function to create voucher and we want to use it."""
        cr, uid = self.cr, self.uid
        refund_id = self.create_credit_note(self.partner_example_00, 20., confirm=True)
        refund_brw = self.invoice.browse(cr, uid, refund_id)
        date = fields.date.today()
        num = 53658
        voucher_id = self.invoice.create_check_letter_voucher(
            cr, uid, refund_brw, num, date, self.journal.browse(cr, uid, self.journal_id))
        voucher_read = self.voucher.read(cr, uid, voucher_id, ['reference', 'ax_check_letter_batch_number', 'ax_check_letter_printed'])
        self.assertEqual(voucher_read['reference'], str(num))
        self.assert_(isinstance(voucher_read['ax_check_letter_batch_number'], (int, long)))
        self.assert_(not voucher_read['ax_check_letter_printed'])

    def test_wizard_pay_multi_check_letter(self):
        cr, uid = self.cr, self.uid
        refund_ids = [self.create_credit_note(self.partner_example_00, 20., confirm=True) for i in range(0,5)]
        self.invoice.set_ax_to_pay_check_letter(cr, uid, refund_ids)
        refund_brw_list = self.invoice.browse(cr, uid, refund_ids)
        date = fields.date.today()
        num = 53658
        wizard_pay_c_l = self.registry('ax.pay.check_letter')
        wiz_id = wizard_pay_c_l.create(cr, uid, dict(check_number=num, check_date=date, check_journal_id=self.journal_id))
        context= dict(active_ids=refund_ids)
        wizard_pay_c_l.pay_check_letter(cr, uid, [wiz_id], context=context)
        cr.commit()
        voucher_ids = self.voucher.search(cr, uid, [])
        voucher_read = self.voucher.read(cr, uid, voucher_ids[0], ['ax_check_letter_batch_number', 'ax_check_letter_printed'])
        self.assert_(isinstance(voucher_read['ax_check_letter_batch_number'], (int, long)))
        self.assertEqual(voucher_read['ax_check_letter_printed'], False)
