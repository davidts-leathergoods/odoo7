# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp.tools.amount_to_text import amount_to_text
from datetime import datetime
import math
from openerp import pooler
import time
import string


class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)

        self.current_vouchers = []
        self.current_voucher = None
        self.localcontext.update({
            'get_facture': lambda voucher: self.get_facture(voucher),
            'get_amount': lambda voucher: self.get_amount(voucher),
            'get_date': lambda date: self.get_date(date),
            'get_month_date': lambda date: self.get_month_date(date),
            'get_text': lambda voucher: self._get_text(voucher),
            'get_subject': lambda voucher: self._get_subject(voucher),
            'get_partner_name': lambda voucher: self.get_partner_name(voucher),
            'get_amount_chiffre_star': lambda voucher: self.get_amount_chiffre_star(voucher),
            'store_voucher': lambda voucher: self.store_vouchers(voucher),
            'store_current_voucher': lambda: self.store_current_voucher(),
            'get_current_voucher': lambda: self.return_current_voucher(),
        })
        self.context = context

    def return_current_voucher(self):
        return self.current_voucher

    def store_current_voucher(self):
        """
        Called in the Check part to define the Voucher to use when printing the cheque parts

        :return: True
        """
        self.current_voucher = self.current_vouchers.pop(0)
        return True

    def store_vouchers(self, voucher):
        """
        Used to store used vouchers in the same order as the printed pages

        :return: True
        """
        self.current_vouchers.append(voucher)
        return True

    # On va forcer le changement du '.' par ',': c'est pour respecter le format français.
    # TODO utiliser le bon formatage selon la langue du client ou la langue de la société
    def get_amount_chiffre_star(self, voucher):
        montant = str("%.2f" % abs(voucher.amount))
        star = string.rjust(montant, 10, "*")
        return star.replace(".", ",")

    def get_amount(self, voucher):
        currency = voucher.currency_id
        if currency.name.upper() == 'EUR':
            currency_name = 'Euro'
        elif currency.name.upper() == 'USD':
            currency_name = 'Dollars'
        elif currency.name.upper() == 'BRL':
            currency_name = 'reais'
        else:
            currency_name = currency.name
        # l'appel de la fonction est forcé en français
        # TODO utiliser le bon formatage selon la langue du client ou la langue de la société
        text = "**" + amount_to_text(abs(voucher.amount), voucher.partner_id.lang,  currency_name).upper()
        text = string.ljust(text, 46, "*")
        text += " "
        text = string.ljust(text, 92, "*")
        return text

    def get_facture(self, voucher):
        if voucher.name:
            code = voucher.number + "-" + voucher.name
        else:
            code = voucher.number
        return code

    def get_partner_name(self,voucher):
        if voucher.ax_check_letter_recipient:
           name = voucher.ax_check_letter_recipient.upper()
        else:
           name =  voucher.partner_id.name.upper()
        return string.ljust(name, 45, "*")

    def get_date(self,voucher):
        return datetime.strptime(voucher.date,'%Y-%m-%d').strftime('%d/%m/%Y')

    def get_month_date(self, voucher):
        date = voucher.date
        year = int(date[0:4])
        day = int(date[8:10])
        month = int(date[5:7])
        if month == 1:
            mnth = 'Janvier'
        elif month == 2:
            mnth = 'Février'
        elif month == 3:
            mnth = 'Mars'
        elif month == 4:
            mnth = 'Avril'
        elif month == 5:
            mnth = 'Mai'
        elif month == 6:
            mnth = 'Juin'
        elif month == 7:
            mnth = 'Juillet'
        elif month == 8:
            mnth = 'Aout'
        elif month == 9:
            mnth = 'Septembre'
        elif month == 10:
            mnth = 'Octobre'
        elif month == 11:
            mnth = 'Novembre'
        else:
            mnth = 'Décembre'
        m_date = str(day) + ' ' + str(mnth) + ' ' + str(year)
        return m_date

    def _get_text(self, voucher):
        text = voucher.ax_check_letter_template.body_html
        if text:
            text = text % {
                'partner_name': voucher.partner_id.name,
                'date': time.strftime('%Y-%m-%d'),
                'company_name': voucher.company_id.name,
                'n': '\n'
            }
        return text

    def _get_subject(self, voucher):
        subject = voucher.ax_check_letter_template.subject
        if subject:
            subject = subject % {
                'partner_name': voucher.partner_id.name,
                'date': time.strftime('%Y-%m-%d'),
                'company_name': voucher.company_id.name,
                'n': '\n'
            }
        return subject

report_sxw.report_sxw('report.check_letter', 'account.voucher',
                      'addons/ax_check_letter/report/check_letter.rml',
                      parser=Parser)