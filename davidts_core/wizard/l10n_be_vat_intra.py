import time
import base64

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.report import report_sxw

class partner_vat_intra(osv.osv_memory):
    """
    Partner Vat Intra
    """
    _name = "partner.vat.intra"
    _inherit = "partner.vat.intra"
    _description = 'Partner VAT Intra'


    def create_xml(self, cursor, user, ids, context=None):
        """Creates xml that is to be exported and sent to estate for partner vat intra.
        :return: Value for next action.
        :rtype: dict
        """
        mod_obj = self.pool.get('ir.model.data')
        xml_data = self._get_datas(cursor, user, ids, context=context)
        month_quarter = xml_data['period'][:2]
        year = xml_data['period'][2:]
        data_file = ''

        # Can't we do this by etree?
        data_head = """<?xml version="1.0" encoding="ISO-8859-1"?>
<ns2:IntraConsignment xmlns="http://www.minfin.fgov.be/InputCommon" xmlns:ns2="http://www.minfin.fgov.be/IntraConsignment" IntraListingsNbr="1">
    <ns2:Representative>
        <RepresentativeID identificationType="NVAT" issuedBy="%(issued_by)s">%(vatnum)s</RepresentativeID>
        <Name>%(company_name)s</Name>
        <Street>%(street)s</Street>
        <PostCode>%(post_code)s</PostCode>
        <City>%(city)s</City>
        <CountryCode>%(country)s</CountryCode>
        <EmailAddress>%(email)s</EmailAddress>
        <Phone>%(phone)s</Phone>
    </ns2:Representative>""" % (xml_data)
        if xml_data['mand_id']:
            data_head += '\n\t\t<ns2:RepresentativeReference>%(mand_id)s</ns2:RepresentativeReference>' % (xml_data)
        data_comp_period = '\n\t\t<ns2:Declarant>\n\t\t\t<VATNumber>%(vatnum)s</VATNumber>\n\t\t\t<Name>%(company_name)s</Name>\n\t\t\t<Street>%(street)s</Street>\n\t\t\t<PostCode>%(post_code)s</PostCode>\n\t\t\t<City>%(city)s</City>\n\t\t\t<CountryCode>%(country)s</CountryCode>\n\t\t\t<EmailAddress>%(email)s</EmailAddress>\n\t\t\t<Phone>%(phone)s</Phone>\n\t\t</ns2:Declarant>' % (xml_data)
        if month_quarter.startswith('3'):
            data_comp_period += '\n\t\t<ns2:Period>\n\t\t\t<ns2:Quarter>'+month_quarter[1]+'</ns2:Quarter> \n\t\t\t<ns2:Year>'+year+'</ns2:Year>\n\t\t</ns2:Period>'
        elif month_quarter.startswith('0') and month_quarter.endswith('0'):
            data_comp_period+= '\n\t\t<ns2:Period>\n\t\t\t<ns2:Year>'+year+'</ns2:Year>\n\t\t</ns2:Period>'
        else:
            data_comp_period += '\n\t\t<ns2:Period>\n\t\t\t<ns2:Month>'+month_quarter+'</ns2:Month> \n\t\t\t<ns2:Year>'+year+'</ns2:Year>\n\t\t</ns2:Period>'

        data_clientinfo = ''
        for client in xml_data['clientlist']:
            if not client['vatnum']:
                raise osv.except_osv(_('Insufficient Data!'),_('No vat number defined for %s.') % client['partner_name'])
            data_clientinfo +='\n\t\t<ns2:IntraClient SequenceNumber="%(seq)s">\n\t\t\t<ns2:CompanyVATNumber issuedBy="%(country)s">%(vatnum)s</ns2:CompanyVATNumber>\n\t\t\t<ns2:Code>%(code)s</ns2:Code>\n\t\t\t<ns2:Amount>%(amount).2f</ns2:Amount>\n\t\t</ns2:IntraClient>' % (client)

        data_decl = '\n\t<ns2:IntraListing SequenceNumber="1" ClientsNbr="%(clientnbr)s" DeclarantReference="%(dnum)s" AmountSum="%(amountsum).2f">' % (xml_data)

        data_file += data_head + data_decl + data_comp_period + data_clientinfo + '\n\t\t<ns2:Comment>%(comments)s</ns2:Comment>\n\t</ns2:IntraListing>\n</ns2:IntraConsignment>' % (xml_data)
        context['file_save'] = data_file

        model_data_ids = mod_obj.search(cursor, user,[('model','=','ir.ui.view'),('name','=','view_vat_intra_save')], context=context)
        resource_id = mod_obj.read(cursor, user, model_data_ids, fields=['res_id'], context=context)[0]['res_id']

        return {
            'name': _('Save'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'partner.vat.intra',
            'views': [(resource_id,'form')],
            'view_id': 'view_vat_intra_save',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }



partner_vat_intra()