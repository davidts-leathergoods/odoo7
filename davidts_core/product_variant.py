# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)


class product_variant_dimension_option_davidts(osv.Model):

    _inherit = "product.variant.dimension.option"
    _description = "Dimension Option"

    _columns = {
        'name': fields.char('Dimension Option Name', size=64, required=True, translate=True),
    }
    
product_variant_dimension_option_davidts()