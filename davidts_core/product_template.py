from openerp.osv import fields, osv
from openerp import tools
import logging
_logger = logging.getLogger(__name__)


class DavidtsProductTemplate(osv.osv):

    _name = 'product.template'
    _inherit = 'product.template'

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image_template, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
            return self.write(cr, uid, [id], {'image_template': tools.image_resize_image_big(value)}, context=context)

    _columns = {
        'variant_model_name': fields.char('Variant Model Name', size=64, required=True,
                                          help='[_o.dimension_id.name_] will be replaced by the name of the dimension '
                                               'and [_o.option_id.code_] by the code of the option. Example of Variant'
                                               ' Model Name : "[_o.dimension_id.name_] - [_o.option_id.code_]"'),
        'reference': fields.char('Reference', size=16),
        'old_reference': fields.char('Old reference', size=8),
        'code_generator': fields.char('Code Generator', size=256,
                                      help='enter the model for the product code, all parameter between '
                                           '[_o.my_field_] will be replace by the product field. Example '
                                           'product_code model : prefix_[_o.variants_]_suffixe ==> '
                                           'result : prefix_2S2T_suffix'),
        'packaging_template': fields.one2many('product.packaging', 'template_id', 'Logistical Units',
                                              help="Gives the different ways to package the same product. "
                                                   "This has no impact on the picking order and is mainly used "
                                                   "if you use the EDI module."),
        'image_template': fields.binary("Image", help="This field holds the image used as avatar for this contact, "
                                                      "limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        store={
                                            'product.template': (lambda self, cr, uid, ids, c={}: ids,
                                                                 ['image_template'], 10),
                                        },
                                        help="Medium-sized image of this contact. It is automatically "
                                             "resized as a 128x128px image, with aspect ratio preserved. "
                                             "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image, string="Small-sized image",
                                       type="binary", multi="_get_image",
                                       store={
                                           'product.template': (lambda self, cr, uid, ids, c={}: ids,
                                                                ['image_template'], 10),
                                       }, help="Small-sized image of this contact. It is automatically "
                                               "resized as a 64x64px image, with aspect ratio preserved. "
                                               "Use this field anywhere a small image is required."),

        'product_link_ids': fields.one2many('product.template.link', 'product_id'),
        'metier_id': fields.many2one('davidts.metier', 'Metiers'),
        'inner_material_id': fields.many2one('davidts.inner_material', 'Inner Materials'),
        'outer_material_id': fields.many2one('davidts.outer_material', 'Outer Materials'),
    }
    _defaults = {
        'variant_model_name': lambda*a: '[_o.option_id.name_]',
        'code_generator': "[_'-'.join([x.option_id.code for x in o.dimension_value_ids] or ['CONF'])_]",
    }
    _order = "reference"

    def write(self, cr, uid, ids, vals, context=None):

        product_obj = self.pool.get('product.product')
        product_ids = product_obj.search( cr, uid, [( 'product_tmpl_id', 'in', ids )], context = context )

        if 'description_sale' in vals:
            if not vals.get('description_sale'):
                super(DavidtsProductTemplate, self).write(cr, uid, ids, {'description_sale':''})
                if product_ids:
                  product_obj.write(cr, uid, product_ids, {'description_sale': ''})
            else :
                if product_ids:
                    product_obj.write(cr, uid, product_ids, {'description_sale': vals['description_sale']}, context=context)

        if 'description' in vals:
            if not vals.get('description'):
                super(DavidtsProductTemplate, self).write(cr, uid, ids, {'description':''})
                if product_ids:
                  product_obj.write(cr, uid, product_ids, {'description': ''})

        if 'description_purchase' in vals:
            if not vals.get('description_purchase'):
                super(DavidtsProductTemplate, self).write(cr, uid, ids, {'description_purchase':''})


        res = super(DavidtsProductTemplate, self).write(cr, uid, ids, vals.copy(), context=context)
        return res

DavidtsProductTemplate()


class DavidtsProduct(osv.osv):

    _inherit = 'product.product'

    def generate_product_code(self, cr, uid, product_obj, code_generator, context=None):
        if product_obj.product_tmpl_id.reference:
            return "%s %s" % (product_obj.product_tmpl_id.reference,
                              self.parse(cr, uid, product_obj, code_generator, context=context))
        else:
            return self.parse(cr, uid, product_obj, code_generator, context=context)

DavidtsProduct()


class DavidtsProductPackaging(osv.osv):

    _inherit = 'product.packaging'

    def _calc_volume(self, height, width, length):
        return round(height*width*length,2)

    def _get_volume(self, cr, uid, ids, vals, arg, context=None):
        result = {}
        for packaging in self.browse(cr, uid, ids, context=context):
            result[packaging.id] = self._calc_volume(
                packaging.height, packaging.width, packaging.length)
        return result

    def onchange_volume(self, cr, uid, ids, height, width, length):
        return {'value': {'volume': self._calc_volume(height, width, length)}}

    _columns = {
        'template_id': fields.many2one('product.template', 'Template'),
        'product_id': fields.many2one('product.product', 'Product'),
        'volume': fields.float('Volume'),
    }

    def create(self, cr, uid, vals, context=None):
        vals.update({'volume': self._calc_volume(vals['height'], vals['width'], vals['length'])})
        return super(DavidtsProductPackaging, self).create(cr, uid, vals, context=context)

DavidtsProductPackaging()


class product_customerinfo(osv.osv):

    _name = "product.customerinfo"
    _description = "Information about a product customer"

    _columns = {
        'name': fields.many2one('res.partner', 'Customer', required=True,
                                domain=[('customer', '=', True)], ondelete='cascade',
                                help="Customer of this product"),
        'product_name': fields.char('Customer Product Name', size=128,
                                    help="This Customer's product name will be used when printing a request for "
                                         "quotation. Keep empty to use the internal one."),
        'product_code': fields.char('Customer Product Code', size=64,
                                    help="This Customer's product code will be used when printing a request for "
                                         "quotation. Keep empty to use the internal one."),
        'sequence': fields.integer('Sequence', help="Assigns the priority to the list of product supplier."),
        'product_uom': fields.related('product_id', 'uom_po_id', type='many2one', relation='product.uom',
                                      string="Customer Unit of Measure", readonly="1",
                                      help="This comes from the product form."),
        'min_qty': fields.float('Minimal Quantity', required = True,
                                help="The minimal quantity to purchase to this customer, expressed in the customer "
                                     "Product Unit of Measure if not empty, in the default unit of measure of the "
                                     "product otherwise."),
        'product_id': fields.many2one('product.product', 'Product', required=True, ondelete='cascade', select=True),
        'delay': fields.integer('Delivery Lead Time', required=True,
                                help="Lead time in days between the confirmation of the purchase order and the "
                                     "reception of the products in your warehouse. Used by the scheduler for automatic "
                                     "computation of the purchase order planning."),
        'company_id': fields.many2one('res.company', 'Company', select=1),
    }
    _defaults = {
        'sequence': lambda *a: 1,
        'delay': lambda *a: 1,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'product.customerinfo', context=c),
    }

product_customerinfo()