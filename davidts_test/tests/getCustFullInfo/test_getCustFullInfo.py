from openerp_jsonrpc_client import *
OE_BASE_SERVER_URL = "http://localhost:8069"
server = OpenERPJSONRPCClient(OE_BASE_SERVER_URL)
session_info = server.session_authenticate('davidts', 'admin', 'd@vidts', OE_BASE_SERVER_URL)

partner_obj = server.get_model('res.partner')

if False:
	try:
	    cust_full_info = partner_obj.get_customer_full_info(999999)  # AD SCHILPEROORT
	    print cust_full_info

	except:
	    print "message: %s" % exc.message
	    print "data: %s" % exc.data
	    print "data.type: %s" % exc.data['type']
	    print "data.fault_code: %s" % exc.data['fault_code']

try:
    partner_obj = server.get_model('res.partner')
    cust_full_info = partner_obj.get_customer_full_info(63)  # AD SCHILPEROORT
    print cust_full_info

    cust_full_info = partner_obj.get_customer_full_info(29)  # 4 OFFICE BVBA
    print cust_full_info



except OpenERPJSONRPCClientException as exc:
    print "message: %s" % exc.message
    print "data: %s" % exc.data
    print "data.type: %s" % exc.data['type']
    print "data.fault_code: %s" % exc.data['fault_code']
    raise exc