from openerp.osv import fields, osv

 
class DavidtsMetier(osv.osv):
    _name = 'davidts.metier'
    _inherit = 'davidts.metier'
    _columns = {
        'enable_measure_capacity': fields.boolean('Enable Capacity'),
        'enable_measure_payload': fields.boolean('Enable Payload'),
        'enable_wheel': fields.boolean('Enable wheels'),

        'enable_luggage_business' : fields.boolean('Enable business luggage'),
        'enable_luggage_travel' : fields.boolean('Enable travel luggage'),
        
        'enable_dimension' : fields.boolean('Enable dimension'),
        'enable_garantee': fields.boolean('Enable Garantee', help="Garantee: Exp. 3"),
        'enable_pocket': fields.boolean('Enable Inside pocket with zip', help="Inside pocket with zip (1, 2, 3)"),
        'enable_compartment_sorter': fields.boolean('EnableSorter', help="Insulated compartment (7.1, 7.2, 7.3, ...)"),
        'enable_pocket_floating': fields.boolean('Enable Floating pocket', help="Floating pocket (7.1, 7.2, 7.3, ...)"),

        'enable_computer': fields.boolean('Enable Compartment for laptop?', help="Presence of computer compartment ?"),
 
        'enable_tablet': fields.boolean('EnableCompartment for tablet?', help="Presence of tablet compartment ?"),
        
        'enable_clothing_hanger_webbing': fields.boolean('Enable Enable Hangers - Webbings', help="Hangers Compartment ?"),
        'enable_clothing_webbing': fields.boolean('Enable Webbing', help="Fastening straps 'webbing' (1 or 2)"),
 
        'enable_organizer': fields.boolean('Enable Organizer', help="Presence of an organizer ?"),  
        
        'enable_lock': fields.boolean('Enable Lock', help="Lock?"),        
        'enable_lock_tsa': fields.boolean('Enable Lock TSA', help="Lock?"),        
   
        'enable_accessory_rings': fields.boolean('Enable Rings', help="Rings: Exp. 2"),
        'enable_accessory_tag': fields.boolean('Enable Address holder', help="Address holder?"),        
        'enable_accessory_scratchpad': fields.boolean('Enable Scratch pad', help="Scratch pad"),        
        'enable_accessory_calculator': fields.boolean('Enable Calculator', help="Calculator?"),        
        'enable_accessory_elastic': fields.boolean('Enable Elastic', help="Elastic?"),        
        'enable_accessory_mirror': fields.boolean('Enable Mirror', help="Mirror?"),        
        'enable_accessory_shoulderstrap': fields.boolean('Enable Shoulder strap', help="Shoulder strap?"),        
        'enable_accessory_trolley': fields.boolean('Enable Fits on a trolley', help="Fits on a trolley?"),             
       
        'enable_handle_number': fields.boolean('Enable Number of handles', help="Number of handles: Exp. 2"),
        'enable_handle_adjustable': fields.boolean('Enable Adjustable handle', help="Adjustable handle?"),             
        
        'enable_strap': fields.boolean('Enable Strap', help="Strap?"),             
     
        'enable_puller_sections': fields.boolean('Enable How many sections?', help="How many sections?: Exp. 3"),
        'enable_puller_telescopic': fields.boolean('Enable Telescopic handle', help="Telescopic handle?"),             
        'enable_puller_folding': fields.boolean('Enable Handle foldable', help="Handle foldable?"),             
        'enable_puller_adjustable': fields.boolean('Enable Adjustable handle', help="Adjustable handle?"),             
        'enable_puller_fixed': fields.boolean('Enable Fixed handle', help="Fixed handle?"),   
        'enable_platform': fields.boolean('Enable Foldable platform', help="Foldable platform?"), 
        
        'enable_box': fields.boolean('Enable Stackable cases', help="Stackable cases?"),             
    }

