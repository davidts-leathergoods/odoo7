from openerp.osv import fields, osv
from openerp import tools
import logging
_logger = logging.getLogger(__name__)

class ComputeAvailability (osv.osv) :
  _auto = False
  _name = 'report_compute_availability'
  def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_compute_availability')
        cr.execute("""create or replace view report_compute_availability as (
        select sum(product_qty) qty, default_code,product_id , uom_id, uom_name from (
                select  round(sum( (stock_move.product_qty / stock_move_uom.factor) * product_template_uom.factor) ,0 ) as product_qty,
                    product_product.default_code default_code, 
                    product_product.id product_id,  
                    product_template_uom.id uom_id , 
                    product_template_uom.name uom_name
            from stock_move 
                join product_uom stock_move_uom on stock_move.product_uom = stock_move_uom.id 
                join stock_location on stock_move.location_dest_id = stock_location.id 
                join product_product on stock_move.product_id = product_product.id
                join product_template on product_product.product_tmpl_id = product_template.id
                join product_uom product_template_uom on product_template.uom_id = product_template_uom.id
            where stock_move.state not in ('draft','cancel') and stock_location.usage ='internal'
            group by product_product.default_code , product_product.id ,product_template_uom.id,product_template_uom.name
        union all
            select  - round(sum( (stock_move.product_qty / stock_move_uom.factor) * product_template_uom.factor),0) as product_qty,
                product_product.default_code default_code, 
                product_product.id product_id,  
                product_template_uom.id uom_id , 
                product_template_uom.name uom_name
            from stock_move 
                join product_uom stock_move_uom on stock_move.product_uom = stock_move_uom.id 
                join stock_location on stock_move.location_id = stock_location.id 
                join product_product on stock_move.product_id = product_product.id
                join product_template on product_product.product_tmpl_id = product_template.id
                join product_uom product_template_uom on product_template.uom_id = product_template_uom.id
            where stock_move.state not in ('draft','cancel') and stock_location.usage ='internal'
            group by product_product.default_code , product_product.id ,product_template_uom.id,product_template_uom.name
        ) as move_prev
            group by default_code,uom_id,product_id , uom_name
            order by default_code)
        """)
            
            
            
            
            
    


class DavidtsProductWheels(osv.osv):

    _name = 'product.product.wheel'

    _columns = {
        'name': fields.char('Name',size=128, required=True),
        'code': fields.char('Code', size=2, required=True),
    }
   
DavidtsProductWheels()

class DavidtsProductLuggages(osv.osv):

    _name = 'product.product.luggage'

    _columns = {
        'name': fields.char('Name',size=128, required=True),
        'code': fields.char('Code', size=2, required=True),
    }
   
DavidtsProductLuggages()

class DavidtsProductComputerSize(osv.osv):

    _name = 'product.product.computer_size'

    _columns = {
        'name': fields.char('Name',size=128, required=True),
    }

class DavidtsProductTabletSize(osv.osv):

    _name = 'product.product.tablet_size'

    _columns = {
        'name': fields.char('Name',size=128, required=True),
    }
    
    
DavidtsProductComputerSize()


class DavidtsProductLock(osv.osv):

    _name = 'product.product.lock'

    _columns = {
        'name': fields.char('Name',size=128, required=True),
        'code': fields.char('Code', size=2, required=True),
    }
   
DavidtsProductLock()

class DavidtsProductBox(osv.osv):

    _name = 'product.product.box'

    _columns = {
        'name': fields.char('Name',size=128, required=True),
        'code': fields.char('Code', size=2, required=True),
    }
   
DavidtsProductBox()

class DavidtsProductInsert(osv.osv):

    _name = 'product.product.insert'

    _columns = {
        'name': fields.char('Name',size=128, required=True),
        'code': fields.char('Code', size=2, required=True),
    }
   
DavidtsProductInsert()


class DavidtsProductWinder(osv.osv):

    _name = 'product.product.winder'

    _columns = {
        'name': fields.char('Name',size=128, required=True),
        'code': fields.char('Code', size=2, required=True),
    }
   
DavidtsProductWinder()


class DavidtsProductCompany(osv.osv):

    _name = 'product.product.company'

    _columns = {
        'name': fields.char('Name',size=128, required=True),
        'code': fields.char('Code', size=2, required=False),
        'luggage_h': fields.float('Luggage H', required=False),
        'luggage_l': fields.float('Luggage L', required=False),
        'luggage_p': fields.float('Luggage P', required=False),
        'luggage_total' :fields.float('Total', required=False)
    }
   
DavidtsProductCompany()



class DavidtsProductTemplate(osv.osv):

    _name = 'product.template'
    
    _inherit = 'product.template'
    
    def _compute_accepting_airlines (self,cr,uid,ids,fields,args,context):
        
        templates = self.browse(cr,uid,ids)
        
        proxy_company = self.pool.get('product.product.company')
        cids = proxy_company.search(cr,uid,[],order="name")
        companies = proxy_company.read(cr,uid,cids)
        res = {}
        
        for t in templates :
            
            if t.luggage_cabin :
                cres = []
                for c in companies :
                    if t.height <= c['luggage_h'] and t.width <= c['luggage_p'] and t.length <= c['luggage_l'] and (c['luggage_total'] == 0 or (t.length+t.width+t.height <= c['luggage_total'])) :
                        cres.append (c['name'])
                res[t.id] = ','.join(cres) 
            else : 
                res[t.id]= False
        return res
    
    def _detect_company_change (self,cr,uid,ids,context) :
        proxy_templates = self.pool.get('product.template')
        tids = proxy_templates.search(cr,uid,[])
      
        return tids
    #'product.product' : (_detect_luggage_change,['luggage_cabin','width','height','length'],1),                                 
    #def _detect_luggage_change (self,cr,uid,ids,context) :
    #     print "detect product change"
    #    
    #     proxy_product = self.pool.get('product.product')
    #     products = proxy_product.browse(cr,uid,ids)
    #     res = []
    #     for p in products :
    #         res.append(p.product_tmpl_id.id)
    #     return res
         
    def _detect_luggage_change_t (self,cr,uid,ids,context) :
 
        return ids
    
    _columns = {
        'measure_capacity': fields.float('Capacity', help="Liter capacity (content): Exp. 25",select=True),
        'measure_payload': fields.integer('Payload', help="Payload (maximum weight allowed): Exp. 25",select=True),
        'wheel_number': fields.integer('Numbers of wheels', help="Numbers of wheels: Exp. 1",select=True),
        'wheel_diameter_front': fields.float('Front wheel size', help="Diameters of the wheels (different diameter to the front and rear wheels possible!): Exp. 7",select=True),
        'wheel_diameter_rear': fields.float('Rear wheel size', help="Diameters of the wheels (different diameter to the front and rear wheels possible!): Exp. 7",select=True),
 
        'wheel_relativeweight': fields.float('Relative weight (g/l)', help="Relative weight ( weight / capacity) (grams per liter ): Exp. 5 g/l",select=True),
        'wheel_front': fields.many2one('product.product.wheel', 'Front Wheels', domain=[('code','=','WF')], help="Front wheel multidirectional (single / double)",select=True),
        'wheel_back': fields.many2one('product.product.wheel', 'Back Wheels',domain=[('code','=','WB')],help="Fixed or multidirectional rear wheels (level 1)",select=True),
        'wheel_fixed': fields.many2one('product.product.wheel', 'Single or star wheels?',domain=[('code','=','WX')], help="If fixed wheels -> Simple or star",select=True),
        'wheel_multidirectional': fields.many2one('product.product.wheel', 'Single or double?',domain=[('code','=','WM')], help="If multidirectional wheels -> single or double",select=True),
        'wheel_ballbearing': fields.many2one('product.product.wheel', 'Ball bearing',domain=[('code','=','WR')], help="Roulements",select=True),
        'wheel_staircase': fields.boolean('Easily climb stairs?',help="Smooth crossing of stairs",select=True),
        'wheel_easyrepair': fields.boolean('Easyrepair ?', help="Repairable wheels (easyrepair)",select=True),
        'wheel_removable': fields.boolean('Removable wheels', help="Detachable wheels",select=True),
#        'luggage_airlines': fields.many2one('product.product.luggage', 'Cabin case according to airlines',domain=[('code','=','LA')], help="If cabin baggage : Which company ?"),
         #      'product_template' : (_detect_lugage_change,['luggage_cabin','width','height','length'],10),
                                 
        'luggage_accepting_airlines' : fields.function (_compute_accepting_airlines,type='char',string="Accepted by",
                                store= {
                                        'product.template' : (_detect_luggage_change_t,['luggage_cabin','width','height','length'],1),
                                   
                                        'product.product.company': (_detect_company_change, ['name','code','luggage_h','luggage_l','luggage_p','luggage_total'], 10 ) ,
                                   
                                        } 
                        ,select=True 
                        ),
        'height': fields.float('Height', help="Height",select=True),
        'length': fields.float('Length', help="Length",select=True),
        'width': fields.float('Width', help="Width",select=True),
     
        
        'luggage_hand': fields.boolean('Handbag ?', help="Handbag",select=True),
        'luggage_cabin': fields.boolean('Cabin baggage ?', help="Cabin baggage",select=True),
        'luggage_hold': fields.boolean('Checked baggage ?', help="Hold baggage",select=True),
        'luggage_hold_comment' : fields.char('Luggage hold comments',select=True),
        'garantee': fields.integer('Garantee', help="Garantee: Exp. 3",select=True),
        'pocket_insidezipper': fields.integer('Inside pocket with zip', help="Inside pocket with zip (1, 2, 3)",select=True),
        'pocket_insidesliding': fields.integer('Inside pocket without zip', help="Inside pocket without zip",select=True),
        'pocket_ousidezipper': fields.integer('Outside pocket with zip', help="Outside pocket with zip (1, 2, 3)",select=True),
        'pocket_outsidesliding': fields.integer('Outside pocket without zip', help="Outside pocket without zip",select=True),
        'compartment': fields.integer('Number of compartments?', help="Number of compartments  (1,2, etc.)",select=True),
        'compartment_expandable': fields.boolean('Expandable compartment', help="Expandable compartment (7.1, 7.2, 7.3, ...)",select=True),
        'compartment_insulated': fields.boolean('Insulated compartment', help="Insulated compartment' (7.1, 7.2, 7.3, ...)",select=True),
        'compartment_sorter': fields.boolean('Sorter', help="Insulated compartment (7.1, 7.2, 7.3, ...)",select=True),
        'pocket_floating': fields.boolean('Floating pocket', help="Floating pocket (7.1, 7.2, 7.3, ...)",select=True),
        'computer': fields.boolean('Compartment for laptop?', help="Presence of computer compartment ?",select=True),
        'computer_height': fields.float('Computer height', help="Computer height :Exp. 35",select=True),
        'computer_length': fields.float('Computer length', help="Computer length: Exp. 27",select=True),
        'computer_width': fields.float('Computer width', help="Computer width: Exp. 24",select=True),
        'computer_size': fields.many2one('product.product.computer_size', 'Computer size', help="Computer size: Exp. 15 pouces",select=True),
        'tablet': fields.boolean('Compartment for tablet?', help="Presence of tablet compartment ?",select=True),
        'tablet_height': fields.float('Tablet height', help="Tablet height: Exp. 25",select=True),
        'tablet_width': fields.float('Tablet width', help="Tablet width: Exp. 15",select=True),
        'tablet_size': fields.many2one('product.product.tablet_size', 'Tablet size', help="Tablet size: Exp. 8 pouces",select=True),
        
        'clothing_hanger': fields.boolean('Hangers', help="Hangers Compartment ?",select=True),
        'clothing_webbing': fields.integer('Webbing', help="Fastening straps 'webbing' (1 or 2)",select=True),
        'organizer': fields.boolean('Organizer', help="Presence of an organizer ?",select=True),  
        'lock': fields.boolean('Lock', help="Lock?",select=True),        
        'lock_tsa': fields.boolean('TSA lock', help="TSA Lock ?",select=True),        
        'lock_easychange': fields.boolean('Easychange lock?', help="Easychange lock?",select=True),
        'lock_type': fields.many2one('product.product.lock', 'Padlock or lock?',domain=[('code','=','LT')], help="Padlock or lock? (fixe | cadenas)",select=True),
        'lock_tsa_type': fields.many2one('product.product.lock', 'Combination or key?',domain=[('code','=','LS')], help="Combination or key?",select=True),
        'accessory_rings': fields.integer('Rings', help="Rings: Exp. 2",select=True),
        'accessory_tag': fields.boolean('Address holder', help="Address holder?",select=True),        
        'accessory_scratchpad': fields.boolean('Scratch pad', help="Scratch pad",select=True),        
        'accessory_calculator': fields.boolean('Calculator', help="Calculator?",select=True),        
        'accessory_elastic': fields.boolean('Elastic', help="Elastic?",select=True),        
        'accessory_mirror': fields.boolean('Mirror', help="Mirror?",select=True),        
        'accessory_shoulderstrap': fields.boolean('Shoulder strap', help="Shoulder strap?",select=True),        
        'accessory_trolley': fields.boolean('Fits on a trolley', help="Fits on a trolley?",select=True),             
        'handle_number': fields.integer('Number of handles', help="Number of handles: Exp. 2",select=True),
        'handle_adjustable': fields.boolean('Adjustable handle', help="Adjustable handle?",select=True),             
        'strap': fields.boolean('Strap', help="Strap?",select=True),             
        'strap_chest': fields.boolean('Chest strap', help="Chest strap?",select=True),             
        'strap_hip': fields.boolean('Hip strap', help="Hip strap?",select=True),             
        'strap_compression': fields.boolean('Compression strap', help="Compression strap?",select=True),  
        'puller_sections': fields.integer('How many sections?', help="How many sections?: Exp. 3",select=True),
        'puller_telescopic': fields.boolean('Telescopic handle', help="Telescopic handle?",select=True),             
        'puller_folding': fields.boolean('Handle foldable', help="Handle foldable?",select=True),             
        'puller_adjustable': fields.boolean('Adjustable handle', help="Adjustable handle?",select=True),             
        'puller_fixed': fields.boolean('Fixed handle', help="Fixed handle?",select=True),   
        'platform': fields.boolean('Foldable platform', help="Foldable platform?",select=True), 
        'box_stackable': fields.boolean('Stackable cases', help="Stackable cases?",select=True),             
        'box_type': fields.many2one('product.product.box', 'What kind of boxes?',domain=[('code','=','BT')], help="What kind of boxes? (bijoux | montres | maquillage, ..)",select=True),
        'box_implement': fields.integer('How many elements can we store?', help="How many elements can we store?: Exp. 10",select=True),
        'box_tray': fields.integer('How many trays?', help="How many trays?: Exp. 3",select=True),
        'box_drawer': fields.integer('How many drawer?', help="How many drawer?: Exp. 3",select=True),
        'box_lid': fields.many2one('product.product.box', 'What kind of lid?', domain=[('code','=','BL')], help="What kind of lid?(vitre, plein, ..)",select=True),
        'box_tray_type': fields.many2one('product.product.box', 'What kind of tray?',domain=[('code','=','BY')], help="What kind of tray? (fixe, amovible, automatique, ..)",select=True),
        'box_drawer_type': fields.many2one('product.product.box', 'What kind of drawer?',domain=[('code','=','BD')], help="What kind of drawer? (automatique | non auto | ..)",select=True),
        'case_type': fields.many2one('product.product.box', 'What kind of cases?',domain=[('code','=','BC')], help="What kind of cases?(manucure | cirage | couture | cravatte | chassures ..)",select=True),
        'case_closing': fields.many2one('product.product.box', 'What kind of closing?',domain=[('code','=','BS')], help="What kind of closing? (fermoir,pression,tirette ..)",select=True),
        'insert': fields.boolean('Insert', help="Insert?"),
        'insert_type': fields.many2one('product.product.insert', 'What kind of insert?',domain=[('code','=','IT')], help="What kind of insert? (rigide | etuis ..)",select=True),
        'insert_number': fields.integer('How many inserts?', help="How many inserts?: Exp. 1",select=True),
        'watchwinder_watchs': fields.integer('Number of watches', help="Number of watches: Exp. 4",select=True),
        'watchwinder_programs': fields.integer('How many programs?', help="How many programs?: Exp. 3",select=True),
        'watchwinder_compartment': fields.integer('Additional compartment?', help="Additional compartment?: Exp. 1",select=True),
        'watchwinder_timer': fields.boolean('Timer', help="Timer?",select=True),
        'watchwinder_plug': fields.many2one('product.product.winder', 'Plug or power supply?',domain=[('code','=','WP')], help="Plug or power supply (pile | secteur | pile et secteur..)",select=True),
        
        'weight': fields.float('Weight', help="Weight",select=True),
        
        'enable_measure_capacity': fields.related('metier_id','enable_measure_capacity'  ,type="boolean",string='Capacity'),
        'enable_measure_payload': fields.related('metier_id','enable_measure_payload'  ,type="boolean",string='Payload'),
        'enable_wheel': fields.related('metier_id','enable_wheel'  ,type="boolean",string='Enable wheels'),

        'enable_luggage_business' : fields.related('metier_id','enable_luggage_business' ,type="boolean",string='Business luggage'),
        'enable_luggage_travel' : fields.related('metier_id','enable_luggage_travel'  ,type="boolean",string='Business luggage'),
        
        'enable_dimension' : fields.related('metier_id','enable_dimension'  ,type="boolean",string='Enable business luggage',select=True),
        'enable_garantee': fields.related('metier_id','enable_garantee'  ,type="boolean",string='Enable Garantee', help="Garantee: Exp. 3"),
        'enable_pocket': fields.related('metier_id','enable_pocket'  ,type="boolean",string='Inside pocket with zip', help="Inside pocket with zip (1, 2, 3)"),
        'enable_compartment_sorter': fields.related('metier_id','enable_compartment_sorter'  ,type="boolean",string='Sorter', help="Insulated compartment (7.1, 7.2, 7.3, ...)"),
        'enable_pocket_floating': fields.related('metier_id','enable_pocket_floating'  ,type="boolean",string='Floating pocket', help="Floating pocket (7.1, 7.2, 7.3, ...)"),

        'enable_computer': fields.related('metier_id','enable_computer' ,type="boolean",string='Compartment for laptop?', help="Presence of computer compartment ?"),
 
        'enable_tablet': fields.related('metier_id','enable_tablet'  ,type="boolean",string='Compartment for tablet?', help="Presence of tablet compartment ?"),
        
        'enable_clothing_hanger_webbing': fields.related('metier_id','enable_clothing_hanger_webbing'  ,type="boolean",string='Enable Hangers - Webbings', help="Hangers Compartment ?"),
        'enable_clothing_webbing': fields.related('metier_id','enable_clothing_webbing'  ,type="boolean",string='Webbing', help="Fastening straps 'webbing' (1 or 2)"),
 
        'enable_organizer': fields.related('metier_id','enable_organizer'  ,type="boolean",string='Organizer', help="Presence of an organizer ?"),  
        
        'enable_lock': fields.related('metier_id','enable_lock'  ,type="boolean",string='Lock', help="Lock?"),        
        'enable_lock_tsa': fields.related('metier_id','enable_lock_tsa'  ,type="boolean",string='Lock TSA', help="Lock?"),        
   
        'enable_accessory_rings': fields.related('metier_id','enable_accessory_rings'  ,type="boolean",string='Rings', help="Rings: Exp. 2"),
        'enable_accessory_tag': fields.related('metier_id','enable_accessory_tag'  ,type="boolean",string='Address holder', help="Address holder?"),        
        'enable_accessory_scratchpad': fields.related('metier_id','enable_accessory_scratchpad' ,type="boolean",string='Scratch pad', help="Scratch pad"),        
        'enable_accessory_calculator': fields.related('metier_id','enable_accessory_calculator'  ,type="boolean",string='Calculator', help="Calculator?"),        
        'enable_accessory_elastic': fields.related('metier_id','enable_accessory_elastic'  ,type="boolean",string='Elastic', help="Elastic?"),        
        'enable_accessory_mirror': fields.related('metier_id','enable_accessory_mirror'  ,type="boolean",string='Mirror', help="Mirror?"),        
        'enable_accessory_shoulderstrap': fields.related('metier_id','enable_accessory_shoulderstrap'  ,type="boolean",string='Shoulder strap', help="Shoulder strap?"),        
        'enable_accessory_trolley': fields.related('metier_id','enable_accessory_trolley'  ,type="boolean",string='Fits on a trolley', help="Fits on a trolley?"),             
       
        'enable_handle_number': fields.related('metier_id','enable_handle_number'  ,type="boolean",string='Number of handles', help="Number of handles: Exp. 2"),
        'enable_handle_adjustable': fields.related('metier_id','enable_handle_adjustable'  ,type="boolean",string='Adjustable handle', help="Adjustable handle?"),             
        
        'enable_strap': fields.related('metier_id','enable_strap'  ,type="boolean",string='Strap', help="Strap?"),             
     
        'enable_puller_sections': fields.related('metier_id','enable_puller_sections'  ,type="boolean",string='How many sections?', help="How many sections?: Exp. 3"),
        'enable_puller_telescopic': fields.related('metier_id','enable_puller_telescopic'  ,type="boolean",string='Telescopic handle', help="Telescopic handle?"),             
        'enable_puller_folding': fields.related('metier_id','enable_puller_folding'  ,type="boolean",string='Handle foldable', help="Handle foldable?"),             
        'enable_puller_adjustable': fields.related('metier_id','enable_puller_adjustable'  ,type="boolean",string='Adjustable handle', help="Adjustable handle?"),             
        'enable_puller_fixed': fields.related('metier_id','enable_puller_fixed'  ,type="boolean",string='Fixed handle', help="Fixed handle?"),   
        'enable_platform': fields.related('metier_id','enable_platform'  ,type="boolean",string='Foldable platform', help="Foldable platform?"), 
        
        'enable_box': fields.related('metier_id','enable_box' ,type="boolean",string='Stackable cases', help="Stackable cases?")            

    
    }
    
    
    _defaults = {
            'wheel_staircase':False,
            'wheel_easyrepair':False,
            'wheel_removable':False,
            'luggage_hand':False,
            'luggage_cabin':False,
            'luggage_hold':False,
            'compartment_expandable':False,
            'compartment_insulated':False,
            'compartment_sorter':False,
            'pocket_floating':False,
            'computer':False,
            'tablet':False,
            'clothing_hanger':False,
            'organizer':False,
            'lock':False,
            'lock_tsa':False,
            'lock_easychange':False,
            'accessory_tag':False,
            'accessory_scratchpad':False,
            'accessory_calculator':False,
            'accessory_elastic':False,
            'accessory_mirror':False,
            'accessory_shoulderstrap':False,
            'accessory_trolley':False,
            'handle_adjustable':False,
            'strap':False,
            'strap_chest':False,
            'strap_hip':False,
            'strap_compression':False,
            'puller_telescopic':False,
            'puller_folding':False,
            'puller_adjustable':False,
            'puller_fixed':False,
            'platform':False,
            'box_stackable':False,
            'box_lid':False,
            'insert':False,
            'insert':False,
        }
    
   
DavidtsProductTemplate()