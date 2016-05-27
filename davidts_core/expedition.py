# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from tempfile import TemporaryFile
import base64


class stock_move(osv.osv):

    _inherit = 'stock.move'

    def _get_reference(self, cr, uid, ids, field, arg, context=None):
        customer_obj = self.pool.get('product.customerinfo')
        result = {}
        for id in ids:
            delivery_order_line = self.browse(cr, uid, id, context)
            if delivery_order_line:
                product_ids = customer_obj.search(cr, uid, [('product_id', '=', delivery_order_line.product_id.id),
                                                            ('name', '=', delivery_order_line.partner_id.id)], context=context)
                if product_ids:
                    result[id] = customer_obj.browse(cr, uid, product_ids[0], context).product_code
        return result

    _columns = {
        'tracking_from': fields.integer('Tracking from'),
        'tracking_to': fields.integer('Tracking to'),
        'reference': fields.function(_get_reference, store=True, String="Reference", type="char"),

        }
    _defaults = {
        'tracking_from': 1,
        'tracking_to': 1,
        }

stock_move()


class davidts_stock_move(osv.osv):
    _inherits = {'stock.move': 'stock_move_id'}
    _name = "davidts.stock.move"
    _columns = {
        'expedition_id': fields.many2one('davidts.expedition', 'Expedition'),
        'stock_move_id': fields.many2one('stock.move', 'Stock move'),

        }
davidts_stock_move()


class davidts_expedition(osv.osv):

    _name = "davidts.expedition"
    _inherit = ['mail.thread']

    def _get_warning_package_number(self, cr, uid, ids, name, args, context=None):
        result = {}
        for id in ids:
            expedition = self.browse(cr, uid, id, context)
            result[id] = "True"
            sum = 0
            if expedition.exp_line_ids:
                list = []
                for line in expedition.exp_line_ids:
                    sum += line.tracking_to - line.tracking_from + 1
                    for i in range(line.tracking_from+1, line.tracking_to):
                        list.append(i)
                    list.append(line.tracking_to)
                    list.append(line.tracking_from)
                lenlist = list.__len__()
                lenset = set(list).__len__()
                if lenlist != lenset:
                    sum = lenset
                if sum != expedition.package_nb:
                    result[id] = "False"
        return result

    _columns = {
        'create_date': fields.datetime("Create date"),
        'name': fields.char('Packing List', readonly=True),
        'transporter': fields.many2one('res.partner', string='Transporter', required=True),
        'invoice_partner_id': fields.many2one('res.partner', string='Invoice partner'),
        'expedition_adr': fields.many2one('res.partner', string='Expedition Address', required=True),
        'parent_expedition_adr': fields.many2one('res.partner', string='Expedition Address', required=True),
        'package_nb': fields.integer(string='Package Number'),
        'to_print': fields.integer(string='To print'),
        'palette_nb': fields.integer(string='Palette Number'),
        'total_weight': fields.float(string='Total weight'),
        'exp_line_ids': fields.one2many('davidts.stock.move', 'expedition_id', string='Colis'),
        'stock_picking_out_ids': fields.many2many('stock.picking.out', 'davidts_picking_exp_rel', 'expedition_id',
                                                  'picking_id', string='Bon de livraison',
                                                  domain=[('state', 'not in', ['cancel']),
                                                          ('type', '=', 'out')]),
        'note': fields.text('Notes'),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Done')], 'State', select=True, readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, select=1),
        'warning_package_number': fields.function(_get_warning_package_number, type='char', readonly=True,
                                                  string="warning_package_number"),
        }

    _defaults = {
        'name': '/',
        'to_print': 1,
        'palette_nb': 1,
        'state': 'draft',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'davidts.expedition', context=c),
        }

    _order = "name desc"

    def default_get(self, cr, uid, fields, context=None):
        res = super(davidts_expedition, self).default_get(cr, uid, fields, context)
        if context and context.get('expedition_adr'):
            part_obj = self.pool.get('res.partner')
            expedition_adr1= part_obj.search(cr, uid, [('parent_id', '=', context.get('expedition_adr')),('type','=','delivery'),('shipping_adress_sequence','=',1)])
            expedition_adr2= part_obj.search(cr, uid, [('parent_id', '=', context.get('expedition_adr')),('type','=','delivery'),('shipping_adress_sequence','=',5)])
            if expedition_adr1:
                expedition_adr = expedition_adr1[0]
            else:
                if expedition_adr2:
                    expedition_adr = expedition_adr2[0]
                else:
                    expedition_adr = context.get('expedition_adr')


            res.update({'expedition_adr': expedition_adr,
                        'invoice_partner_id': context.get('expedition_adr')})
        return res

    def recuperate_package_list(self, cr, uid, ids, context=None):
        stock_move_obj = self.pool.get('davidts.stock.move')
        for id in ids:
            expedition = self.browse(cr, uid, id, context)
            for record in expedition.stock_picking_out_ids:
                for line in record.move_lines:
                    d_stock_move_ids = stock_move_obj.search(cr, uid, [('expedition_id', '=', id),
                                                                       ('stock_move_id', '=', line.id)])
                    if d_stock_move_ids:
                        stock_move_obj.write(cr, uid, d_stock_move_ids, {'expedition_id': id,
                                                                         'stock_move_id': line.id})
                    else:
                        stock_move_obj.create(cr, uid, {'expedition_id': id, 'stock_move_id': line.id})
        return True

    def confirm_liste_colisage(self, cr, uid, ids, context=None):
        name = self.pool.get('ir.sequence').next_by_code(cr, uid, 'davidts.expedition', context)
        return self.write(cr, uid, ids, {'name': name, 'state': 'done'})

    def onchange_package_nb(self, cr, uid, ids, package_nb, context=None):
        return {'value':  {'to_print': package_nb}}

    def adapt(self, cr, uid, ids, column, length, context=None):
        cl2str = str(column)
        if not column:
            cl2str = ""
            for i in range(length):
                cl2str += " "
        else:
            if cl2str.__len__() != length:
                diff = length - cl2str.__len__()
                if diff > 0:
                    for i in range(diff):
                        cl2str += " "
                else:
                    cl2str = cl2str[:length]
        return cl2str

    def onchange_name(self, cr, uid, ids, name, context):
        res = {}
        if context and context.get('expedition_adr'):
            res['domain'] = {'expedition_adr': [('type', '=', 'delivery'),('parent_id','=',context.get('expedition_adr'))]}
        return res

davidts_expedition()



