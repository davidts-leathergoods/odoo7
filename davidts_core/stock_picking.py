# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
import os
from openerp.tools.translate import _
import logging
from openerp.tools import config 
_logger = logging.getLogger(__name__)
# Evolution #45407

class StockPicking(osv.osv):

    _inherit = 'stock.picking'

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

    def _client_limit_cridit_warning_fn(self, cr, uid, ids, name, args, context=None):
        cur_obj = self.pool.get('res.currency')
        result = {}
        for o in self.browse(cr, uid, ids, context=context):
            result[o.id] = "False"
            amount_untaxed = 0.0
            amount_tax = 0.0
            amount_total = 0.0
            
            val = val1 = 0.0
            if o.sale_id and o.sale_id.pricelist_id and o.sale_id.pricelist_id.currency_id:
                cur = o.sale_id.pricelist_id.currency_id
                for line in o.sale_id.order_line:
                    val1 += line.price_subtotal
                    val += self.pool.get('sale.order')._amount_line_tax(cr, uid, line, context=None)
                amount_tax = cur_obj.round(cr, uid, cur, val)
                amount_untaxed = cur_obj.round(cr, uid, cur, val1)
                amount_total = amount_untaxed + amount_tax
            if o.partner_id and o.partner_id.credit and o.partner_id.credit + amount_total > o.partner_id.credit_limit:                
                result[o.id] = 'True'
        return result

    _columns = {
        'warning': fields.function(_get_warning_message, methode=True, type='text', store=True, readonly=True,
                                   string="Warning"),
        'client_limit_cridit_warning': fields.function(_client_limit_cridit_warning_fn, type='char',
                                                       string='Customer has exceeded their credit limit'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Transfer'),
            ('updated', 'Updated'),
            ('done', 'Transferred'),
        ], 'Status', readonly=True, select=True, track_visibility='onchange', help="""
            * Draft: not confirmed yet and will not be scheduled until confirmed\n
            * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
            * Waiting Availability: still waiting for the availability of products\n
            * Ready to Transfer: products reserved, simply waiting for confirmation.\n
            * Transferred: has been processed, can't be modified or cancelled anymore\n
            * Cancelled: has been cancelled, can't be confirmed anymore"""
               ),
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
        'partner_ref':fields.related('purchase_id','partner_ref',type='char',string='Partner reference'),
    }
    
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        res = super(StockPicking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context)
        res['section_id']=partner.section_id.id
        return res
          
    def _prepare_invoice_group(self, cr, uid, picking, partner, invoice, context=None):
        res = super(StockPicking, self)._prepare_invoice_group(cr, uid, picking, partner, invoice, context)
        res['user_id']=partner.user_id.id
        return res
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        sale_obj = self.pool.get('sale.order')
        res = super(StockPicking, self)._prepare_invoice_line(cr, uid, group, picking, move_line,
                                                              invoice_id, invoice_vals, context=None)
        if group:
            name = (picking.name or '') + ' - ' + move_line.name
            if picking.origin:
                sale_ids = sale_obj.search(cr, uid, [('name', '=', picking.origin)])
                if sale_ids:
                    sale = sale_obj.browse(cr, uid, sale_ids[0])
                    if not sale.client_order_ref:
                        name = move_line.name
                    else:
                        name = '%s - %s' % (sale.client_order_ref, move_line.name)
            res.update({'name': name})
        if move_line.sale_line_id:
            if move_line.product_id.id != move_line.sale_line_id.product_id.id:
                res['name'] += ' [' + move_line.sale_line_id.product_id.default_code + ']'
        return res

StockPicking()

class DavidtsStockPickingOut(osv.osv):
    _name = "stock.picking.out"
    _inherit = "stock.picking.out"
    _table = "stock_picking"
    
    def _get_warning_message(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            if obj.partner_id:
                if obj.partner_id.is_company:
                    result[obj.id] = obj.partner_id.warning or False
                elif obj.partner_id.parent_id:
                    if obj.partner_id.type != 'delivery':
                        result[obj.id] = obj.partner_id.parent_id.warning or False
                    else:
                        result[obj.id] = False
                else:
                    result[obj.id] = False
        return result

    def onchange_partner_in(self, cr, uid, ids, partner_id, context=None):
        result = super(DavidtsStockPickingOut, self).onchange_partner_in(cr, uid, ids, partner_id, context=context)
        if partner_id:
            obj = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            if obj.is_company:
                warning = obj.warning or False
            elif obj.parent_id: 
                warning = obj.parent_id.warning or False
            else:
                warning = False
            result['value'] = {'warning': warning}
        return result

    def onchange_min_date(self, cr, uid, ids, min_date,move_lines, context=None):
        res =[]
        for line in move_lines:
            res.append([line[0],line[1],{'date_expected': min_date , 'date': min_date}])
        return {'value': {'move_lines': res}}
    
    def _client_limit_cridit_warning_fn(self, cr, uid, ids, name, args, context=None):
        cur_obj = self.pool.get('res.currency')
        result = {}
        for o in self.browse(cr, uid, ids, context=context):
            result[o.id] = "False"
            amount_untaxed = 0.0
            amount_tax = 0.0
            amount_total = 0.0
            val = val1 = 0.0
            if o.sale_id and o.sale_id.pricelist_id and o.sale_id.pricelist_id.currency_id:
                cur = o.sale_id.pricelist_id.currency_id
                for line in o.sale_id.order_line:
                    val1 += line.price_subtotal
                    val += self.pool.get('sale.order')._amount_line_tax(cr, uid, line, context=None)
                amount_tax = cur_obj.round(cr, uid, cur, val)
                amount_untaxed = cur_obj.round(cr, uid, cur, val1)
                amount_total = amount_untaxed + amount_tax
            if o.partner_id and o.partner_id.credit and o.partner_id.credit + amount_total > o.partner_id.credit_limit:                
                result[o.id] = 'True'
        return result  
    
    def read_wms_stock_picking_out_files(self, cr, uid, ids, context=None):
        parameter_obj = self.pool.get("ir.config_parameter")
        PATH_JOB = '../../project_addons/openerp_wms/sale_openerpwms/sale_openerpwms/sale_openerpwms_run.sh'
        ad_paths = map(lambda m: os.path.abspath(m.strip()),config['addons_path'].split(','))
        _logger.debug("Searching wms import script sale_openerpwms_run.sh")
        for p in ad_paths :
           tsp = p + "/openerp_wms/sale_openerpwms/sale_openerpwms/sale_openerpwms_run.sh"
           if os.path.isfile(tsp) :
                PATH_JOB = tsp
                _logger.debug("Adjusted PATH sale_openerpwms_run to %s" %tsp)
 
        
        if parameter_obj.get_param(cr, uid, "davits.path_openerp_wms"):
            #JMA Mise en commentaire
            #os.system('sh '+  PATH_JOB+" "+parameter_obj.get_param(cr, uid, "davits.path_openerp_wms")+" "+str(ids[0]))
            os.system('sh %s %d' % (PATH_JOB, ids[0]))
        else:
            raise osv.except_osv(_('Warning!'), 
                                   _('WMS files can not be generate. Please specify WMS_files generated path from OpenERP (Settings => Sales => Davidts => Path: WMS files generated)'))
        return
    
    _columns = {
        'warning': fields.function(_get_warning_message, methode=True, type='text', store=True, readonly=True,
                                   string="Warning"),
        'client_limit_cridit_warning': fields.function(_client_limit_cridit_warning_fn, type='char',
                                                       string='limit_cridit_warning'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Transfer'),
            ('updated', 'Updated'),
            ('done', 'Transferred'),
        ], 'Status', readonly=True, select=True, track_visibility='onchange', help="""
            * Draft: not confirmed yet and will not be scheduled until confirmed\n
            * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
            * Waiting Availability: still waiting for the availability of products\n
            * Ready to Transfer: products reserved, simply waiting for confirmation.\n
            * Transferred: has been processed, can't be modified or cancelled anymore\n
            * Cancelled: has been cancelled, can't be confirmed anymore"""
                  ),
    }

DavidtsStockPickingOut()

class stock_picking_in(osv.osv):
    _name = "stock.picking.in"
    _inherit = "stock.picking.in"
    _table = "stock_picking"
    _description = "Incoming Shipments"
    _columns = {
        'state': fields.selection(
            [('draft', 'Draft'),
             ('auto', 'Waiting Another Operation'),
             ('confirmed', 'Waiting Availability'),
             ('assigned', 'Ready to Receive'),
             ('updated', 'Updated'),
             ('done', 'Received'),
             ('cancel', 'Cancelled')],
            'Status', readonly=True, select=True,
            help=""""""),

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
        'partner_ref':fields.char("Partner reference"),
    }
    
    def read_wms_stock_picking_in_files(self, cr, uid, ids, context=None):
        parameter_obj = self.pool.get("ir.config_parameter")
        PATH_JOB = '../../project_addons/openerp_wms/purchase_openerpwms/purchase_openerpwms/purchase_openerpwms_run.sh'
        ad_paths = map(lambda m: os.path.abspath(m.strip()),config['addons_path'].split(','))
        _logger.debug("Searching wms import script sale_openerpwms_run.sh")
        for p in ad_paths :
           tsp = p + "/openerp_wms/sale_openerpwms/sale_openerpwms/sale_openerpwms_run.sh"
           if os.path.isfile(tsp) :
                PATH_JOB = tsp
                _logger.debug("Adjusted PATH purchase_openerpwms_run.sh to %s" %tsp)
        
        if self.pool.get("ir.config_parameter").get_param(cr, uid, "davits.path_openerp_wms"):
            #JMA Mise en commentaire
            #os.system('sh '+PATH_JOB+" "+ parameter_obj.get_param(cr, uid,"davits.path_openerp_wms")+" "+str(ids[0]))
            os.system('sh %s %d' % (PATH_JOB, ids[0]))
        else:
            raise osv.except_osv(_('Warning!'), 
                                   _('WMS files can not be generate. Please specify WMS_files generated path from OpenERP (Settings => Sales => Davidts => Path: WMS files generated)'))
        return

stock_picking_in()
# end Evolution #45407
