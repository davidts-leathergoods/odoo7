from openerp import tools
from openerp.osv import fields,osv
from openerp.addons.decimal_precision import decimal_precision as dp


class report_stock_move(osv.osv):
    
    _inherit = "report.stock.move"
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_stock_move')
        cr.execute("""
            CREATE OR REPLACE view report_stock_move AS (
                SELECT
                        min(sm.id) as id, 
                        date_trunc('day', sm.date_expected) as date,
                        to_char(date_trunc('day',sm.date_expected), 'YYYY') as year,
                        to_char(date_trunc('day',sm.date_expected), 'MM') as month,
                        to_char(date_trunc('day',sm.date_expected), 'YYYY-MM-DD') as day,
                        avg(date(sm.date)-date(sm.create_date)) as day_diff,
                        avg(date(sm.date_expected)-date(sm.create_date)) as day_diff1,
                        avg(date(sm.date)-date(sm.date_expected)) as day_diff2,
                        sm.location_id as location_id,
                        sm.picking_id as picking_id,
                        sm.company_id as company_id,
                        sm.location_dest_id as location_dest_id,
                        sum(sm.product_qty) as product_qty,
                        sum(
                            (CASE WHEN sp.type in ('out') THEN
                                     (sm.product_qty * pu.factor / pu2.factor)
                                  ELSE 0.0 
                            END)
                        ) as product_qty_out,
                        sum(
                            (CASE WHEN sp.type in ('in') THEN
                                     (sm.product_qty * pu.factor / pu2.factor)
                                  ELSE 0.0 
                            END)
                        ) as product_qty_in,
                        sm.partner_id as partner_id,
                        sm.product_id as product_id,
                        sm.state as state,
                        sm.product_uom as product_uom,
                        pt.categ_id as categ_id ,
                        coalesce(sp.type, 'other') as type,
                        sp.stock_journal_id AS stock_journal,
                        sum(
                            (CASE WHEN sp.type in ('in') THEN
                                     (sm.product_qty * pu.factor / pu2.factor) * pt.standard_price
                                  ELSE 0.0 
                            END)
                            -
                            (CASE WHEN sp.type in ('out') THEN
                                     (sm.product_qty * pu.factor / pu2.factor) * pt.standard_price
                                  ELSE 0.0 
                            END)
                        ) as value
                    FROM
                        stock_move sm
                        LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                        LEFT JOIN product_product pp ON (sm.product_id=pp.id)
                        LEFT JOIN product_uom pu ON (sm.product_uom=pu.id)
                          LEFT JOIN product_uom pu2 ON (sm.product_uom=pu2.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                    GROUP BY
                        coalesce(sp.type, 'other'), date_trunc('day', sm.date), sm.partner_id,
                        sm.state, sm.product_uom, sm.date_expected,
                        sm.product_id, pt.standard_price, sm.picking_id,
                        sm.company_id, sm.location_id, sm.location_dest_id, pu.factor, pt.categ_id, sp.stock_journal_id,
                        year, month, day
                    ORDER BY
                        id desc
               )
        """)

report_stock_move()
