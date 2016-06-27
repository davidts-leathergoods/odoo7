# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
import os
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from datetime import date
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(osv.osv):
    
    _inherit = "purchase.order"

    _columns = {
        'event_ids': fields.many2many('evenement.evenement', 'purchase_event_rel', 'purchase_id',
                                      'event_id', 'Event'),
        'charte_id': fields.many2one('charte', 'Charter', required=False),
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm'),
        'delivery_date': fields.date('Delivery date'),
        'delivery_carrier_id': fields.many2one('delivery.carrier', 'Delivery method'),
        'vessel': fields.char('Vessel', size=128),
        'trip_name': fields.char("Trip's name", size=128),
        'conveyance_reference': fields.char('Conveyance reference', size=128),
        'departure_point': fields.char('Departure point', size=128),
        'arrival_point': fields.char('Arrival point', size=128),
        'etd': fields.date('ETD'),
        'eta': fields.date('ETA'),
    }


    def read_wms_purchase_files(self, cr, uid, ids):
        parameter_obj = self.pool.get("ir.config_parameter")
        PATH_JOB = '../../project_addons/openerp_wms/purchase_openerpwms/purchase_openerpwms/purchase_openerpwms_run.sh'
        ad_paths = map(lambda m: os.path.abspath(m.strip()),config['addons_path'].split(','))
        _logger.debug("Searching wms import script purchase_openerpwms_run")
        for p in ad_paths :  
           jsp = p + "/openerp_wms/purchase_openerpwms/purchase_openerpwms/purchase_openerpwms_run.sh"
           if os.path.isfile(jsp) :
                PATH_JOB = jsp
                _logger.debug("Adjusted PATH_JOB to %s"%jsp)
        
        if parameter_obj.get_param(cr, uid, "davits.path_openerp_wms"):
            os.system('sh %s %s %d' % (PATH_JOB, ids[0]))
        else:
            raise osv.except_osv(_('Purchase Order Warning!'),
                                 _('Attention : Le fichier ne peut pas etre generer. Merci de specifier le chemain '
                                   'des fichiers a exporter depuis OpenERP  (Configuration => Sale => Davidts => '
                                   'WMS files path)'))

    def onchange_date_order(self, cr, uid, ids, date_order, context=None):
        for id in ids:
            purchase = self.browse(cr, uid, id, context)
            if purchase.event_ids:
                raise osv.except_osv(_('Purchase Order Warning!'),
                                     _('Attention : This command is related to events, thank you to verify the '
                                         'impact of changing the date on events.'))
        return {}

    def _prepare_order_picking(self, cr, uid, order, context=None):
        vals = super(PurchaseOrder, self)._prepare_order_picking(cr, uid, order, context=context)
        vals.update({
            'delivery_date': order.delivery_date,
            'vessel': order.vessel,
            'trip_name': order.trip_name,
            'conveyance_reference': order.conveyance_reference,
            'departure_point': order.departure_point,
            'arrival_point': order.arrival_point,
            'etd': order.etd,
            'eta': order.eta,
        })
        if order.incoterm_id:
            vals.update({'incoterm_id': order.incoterm_id.id})
        if order.delivery_carrier_id:
            vals.update({'delivery_carrier_id': order.delivery_carrier_id.id})
        return vals

PurchaseOrder()


class davidts_purchase_order_line(osv.osv):
    
    _inherit = "purchase.order.line"
     
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, context=None):
        if context is None:
            context = {}
        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res
        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')
        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update({'lang': lang, 'partner_id': partner_id})
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        dummy, name = product_product.description_get(cr, uid, product_id, context=context_partner)[0]
        if product.description_purchase:
            name += '\n' + product.description_purchase
        res['value'].update({'name': name})
        res['domain'] = {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id

        if product.uom_id.category_id.id != product_uom.browse(cr, uid, uom_id, context=context).category_id.id:
            if context.get('purchase_uom_check') and self._check_product_uom_group(cr, uid, context=context):
                res['warning'] = {'title': _('Warning!'),
                                  'message': _('Selected Unit of Measure does not belong to the same category as '
                                               'the product Unit of Measure.')}
            uom_id = product_uom_po_id

        res['value'].update({'product_uom': uom_id})
        if not date_order:
            date_order = fields.date.context_today(self, cr, uid, context=context)
        supplierinfo = False
        for supplier in product.seller_ids:
            if partner_id and (supplier.name.id == partner_id):
                supplierinfo = supplier
                if supplierinfo.product_uom.id != uom_id:
                    res['warning'] = {'title': _('Warning!'),
                                      'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name}
                min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                if (qty or 0.0) < min_qty: 
                    if qty:
                        res['warning'] = {'title': _('Warning!'),
                                          'message': _('The selected supplier has a minimal quantity set to %s %s, '
                                                       'you should not purchase less.') % (supplierinfo.min_qty,
                                                                                           supplierinfo.product_uom.name)}
                    qty = min_qty
        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        qty = qty or 1.0
        res['value'].update({'date_planned': date_planned or dt})
        if qty:
            res['value'].update({'product_qty': qty})
        if pricelist_id:
            price = product_pricelist.price_get(cr, uid, [pricelist_id],
                                                product.id, qty or 1.0, partner_id or False,
                                                {'uom': uom_id, 'date': date_order})[pricelist_id]
        else:
            price = product.standard_price
        taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        res['value'].update({'price_unit': price, 'taxes_id': taxes_ids})
        return res

    product_id_change = onchange_product_id