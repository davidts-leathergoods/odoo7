from openerp.osv import fields, osv


class account_invoice(osv.osv):

    _inherit = "account.invoice"

    def _calc_escompte(self, amount_untaxed, prompt_payment_discount_rate):
        return amount_untaxed*prompt_payment_discount_rate/100

    def _get_escompte(self, cr, uid, ids, prompt_payment_discount_rate, amount_untaxed, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.partner_id.taux_escompte:
                invoice.prompt_payment_discount_rate = invoice.partner_id.taux_escompte
                result[invoice.id] = self._calc_escompte(invoice.amount_untaxed, invoice.prompt_payment_discount_rate)
            elif invoice.partner_id.taux_escompte == 0:
                discount = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.prompt_payment_discount_rate")
                if discount != "0":
                    result[invoice.id] = self._calc_escompte(invoice.amount_untaxed, invoice.prompt_payment_discount_rate)
                else:
                    result[invoice.id] = self._calc_escompte(invoice.amount_untaxed, 0)

        return result

    def _get_taux_escompte(self, cr, uid, ids, prompt_payment_discount_rate, amount_untaxed, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            if obj.partner_id:
                if obj.partner_id.taux_escompte:
                    result[obj.id] = obj.partner_id.taux_escompte
                else:
                    result[obj.id] = float(self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.prompt_payment_discount_rate") or "0")

        return result

    def onchange_escompte(self, cr, uid, ids, amount_untaxed, prompt_payment_discount_rate):
        res = {'value': {'escompte': self._calc_escompte(amount_untaxed, prompt_payment_discount_rate)}}
        return res

    def _get_warning_message(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            if obj.partner_id:
                if obj.partner_id.is_company:
                    result[obj.id] = obj.partner_id.warning or False
                elif obj.partner_id.parent_id:
                    result[obj.id] = obj.partner_id.parent_id.warning
                else:
                    result[obj.id] = False
        return result

    def _search_my_order(self, cr, invoice_id):
        cr.execute("SELECT order_id FROM sale_order_invoice_rel where invoice_id = %d" % invoice_id)
        return [x[0] for x in cr.fetchall()]

    def _prepare_refund(self, cr, uid, invoice, date=None, period_id=None, description=None, journal_id=None, context=None):
        result = super(account_invoice, self)._prepare_refund(cr, uid, invoice, date, period_id, description, journal_id,context)
        invoice_section_id = self.browse(cr, uid,invoice.id, context).section_id.id
        result['section_id'] = invoice_section_id
        return result
        
    _columns = {
        'prompt_payment_discount_rate': fields.function(_get_taux_escompte, 'Discount rate'),
        'escompte': fields.function(_get_escompte, string="Escompte"),
        'warning': fields.function(_get_warning_message, methode=True, type='text', store=True, readOnly=True,
                                   string="Warning"),
        'davidts_expedition_id': fields.many2one('davidts.expedition', 'Packing list'),
    }

    _defaults = {
        'prompt_payment_discount_rate': lambda self, cr, uid, context: float(self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.prompt_payment_discount_rate") or "0")
    }

    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id = False):
        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        if partner_id:
            warning = False
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if partner.is_company:
                warning = partner.warning or False
            elif partner.parent_id:
                warning = partner.parent_id.warning or False
            result['value']['warning'] = warning
            if partner.user_id:
                result['value']['user_id'] = partner.user_id.id
            if partner.section_id:
                result['value']['section_id'] = partner.section_id.id
            if partner.ref:
                result['value']['name'] = partner.ref

            if type not in ['in_invoice', 'in_refund'] and partner.property_account_receivable:
                result['value']['account_id'] = partner.property_account_receivable.id
            elif partner.property_account_payable:
                result['value']['account_id'] = partner.property_account_payable.id

            if partner.taux_escompte:
                result['value']['prompt_payment_discount_rate'] = partner.taux_escompte
            elif partner.taux_escompte == 0:
                discount = self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.prompt_payment_discount_rate") or "0"
                if float(discount) != 0:
                    result['value']['prompt_payment_discount_rate'] = float(discount)
                    return result
                else:
                    result['value']['prompt_payment_discount_rate'] = partner.taux_escompte
        return result

account_invoice()