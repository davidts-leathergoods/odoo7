# from openerp.osv import fields, osv
# import datetime
# class sale_order_line(osv.osv):
#     _inherit = "sale.order.line"
# 
#     def action_stock_prevu(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         list = []
#         sol = self.browse(cr, uid, ids, context=context)
#         for mv in sol[0].mv_details_ids:
#             list.append(mv.id)
#         """Open the partial picking wizard"""
#         context.update({
# #              'default_product_id' : sol[0].product_id.id,
#              'default_mv_details_ids': list,
#         })
#         return {
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'stock.prevu',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': context,
#             'nodestroy': True,
#         }
# 
#     def action_sol_stock_prevu(self, cr, uid, ids, context=None):
#         obj_mv_details = self.pool.get('sol.mv.details')
#         if context is None:
#             context = {}
#         list = []
#         sol = self.browse(cr, uid, ids, context=context)
#         for mv in sol[0].sol_mv_ids:
#             if mv.mumero_semain >= 0:
#                 list.append(mv.id)
#         i = 0
#         date_planned = datetime.datetime.strptime(sol[0].order_id.date_order, "%Y-%m-%d").date() + datetime.timedelta(days=sol[0].delay or 0.0)
#         while (datetime.datetime.now().date() + datetime.timedelta(days=7*i )) < date_planned:
#             i += 1
#         where = [tuple([sol[0].product_id.id])]
# #        cr.execute('SELECT mumero_semain,sol_product_qty FROM sol_mv_details where product_id = %s and sol_product_qty <> 0;',tuple(where))
#         cr.execute('UPDATE sol_mv_details SET sol_product_qty=0 WHERE product_id = %s;', tuple(where))
#         if datetime.datetime.now().date() > date_planned:
#             obj_mv_details.write(cr, uid, [sol[0].sol_mv_ids[-1].id], {'sol_product_qty': sol[0].product_uom_qty})
#         elif (i >= 0 and i <= 10):
#             obj_mv_details.write(cr, uid, [sol[0].sol_mv_ids[i].id], {'sol_product_qty': sol[0].product_uom_qty})
#         elif i > 10:
#             obj_mv_details.write(cr, uid, [sol[0].sol_mv_ids[10].id], {'sol_product_qty': sol[0].product_uom_qty})
#         """Open the partial picking wizard"""
#         context.update({
# #              'default_product_id' : sol[0].product_id.id,
#              'default_sol_mv_ids': list
#         })
#         return {
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'sol.mv',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'context': context,
#             'nodestroy': True,
#         }
# 
#     def _get_mv_details_ids(self, cr, uid, ids, name, args, context=None):
#         result = {}
#         lines = []
#         for line in self.browse(cr, uid, ids, context=context):
#             lines = []
#             temp_lines = map(lambda x: x.id, line.product_id.mv_details_ids)
#             lines += [x for x in temp_lines]
#             result[line.id] = lines
#         return result
# 
#     def _get_mv_sol_details_ids(self, cr, uid, ids, name, args, context=None):
#         result = {}
#         lines = []
#         for line in self.browse(cr, uid, ids, context=context):
#             lines = []
#             temp_lines = map(lambda x: x.id, line.product_id.sol_mv_details_ids)
#             lines += [x for x in temp_lines]
#             result[line.id] = lines
#         return result
# 
#     def _negatif_fn(self, cr, uid, ids, name, args, context=None):
#         res = {}
#         for line in self.browse(cr, uid, ids, context=context):
#             negatif = ""
#             temp_lines = map(lambda x: x.id, line.product_id.mv_details_ids)
#             for mv in temp_lines:
#                 mv_obj = self.pool.get('mv.details').browse(cr, uid, mv)
#                 if mv_obj.virtual_available_week_fn  < 0:
#                     negatif = "True"
#             res[line.id] = negatif
#         return res
# 
#     _columns = {
#         'stock_negatif': fields.function(_negatif_fn, string='negatif', type='char'),
#         'sol_mv_ids': fields.function(_get_mv_sol_details_ids, type='many2many', relation='sol.mv.details', string='stock'),
#         'mv_details_ids': fields.function(_get_mv_details_ids, type = 'many2many', relation='mv.details', string='stock'),
#      }
# 
# sale_order_line()
