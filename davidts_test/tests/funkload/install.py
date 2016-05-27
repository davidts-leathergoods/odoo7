# coding: utf8

from anybox.funkload.openerp import OpenERPTestCase
from xmlrpclib import Fault

import logging

_logger = logging.getLogger(__name__)


#
# look at server/6.1/openerp/services/web_services.py for a list of db services
#
class ServiceProxy(object):
    """
    A proxy to any OpenERP Service, for Funkload case.
    Outrageously inspired from anybox.openerp.funkload ModelProxy
    Typical use case is for "db" service which allow to create, drop,... databases
    """

    def __init__(self, testcase, service_name):
        self._service_name = service_name
        self._url = testcase.server_url + '/xmlrpc/' + service_name
        self._testcase = testcase

    def __getattr__(self, method):
        """Return a wrapper method ready for Funkload's xmlrpc calls."""
        def proxy(*args, **kw):
            """
            :param args: a list of parameters for methd
            """
            # exception handling is done by Funkload (logs errors etc)
            tc = self._testcase
            description = kw.pop('description', None)
            return tc.xmlrpc(self._url, method, args, description=description)
        return proxy


class BootstrapDB(OpenERPTestCase):

    def setUp(self):
        # Note: setUp() is called before each test
        super(BootstrapDB, self).setUp()
        self.openerp_admin_password = self.conf_get('main', 'openerp_admin_password')
        self.admin_password = self.conf_get('main', 'admin_password')
        self.core_module_name = self.conf_get('main', 'core_module_name')
        self.base_data_module_name = self.conf_get('main', 'base_data_module_name')
        self.test_module_name = self.conf_get('main', 'test_module_name')

    def test_000_drop_db(self):
        """Drop de la database de Dev via OpenERP db service"""
        db_service = ServiceProxy(self, 'db')
        db_exists = db_service.db_exist(self.db_name)
        if db_exists:
            db_service.drop(self.openerp_admin_password, self.db_name)
        else:
            _logger.info("La base %s n'existe pas" % self.db_name )

        if db_exists:
            self.assertFalse(db_service.db_exist(self.db_name), "Base de Développement non droppée")

    def test_010_create_database(self):
        """Creation de la database de Dev"""
        db_service = ServiceProxy(self, 'db')
        db_service.create_database(self.openerp_admin_password, self.db_name, False, 'fr_FR', self.admin_password)
        self.assertTrue(db_service.db_exist(self.db_name), "Base non créée")

    def test_020_login(self):
        """Test login as admin and check uid"""
        self.login('admin', self.admin_password)
        self.assertEqual(self.uid, 1, "Login failed")

    def test_025_set_admin_technical_feature(self):
        """
        Add administrator to the "Technical Features" group
        """
        self.login('admin', self.admin_password)
        group_no_one_id = self.ref('res.groups', 'base', 'group_no_one')
        user_obj = self.model('res.users')
        # [(4 is the command to add a value to existing ones here we add group_no_one_id to the
        # user group list
        user_obj.write([self.uid], {'groups_id': [(4, group_no_one_id)]})


    def test_030_install_account_accountant_module(self):
        """
        Install account_accountant module straight (don't use the installer)
        """
        self.login('admin', self.admin_password)
        module_obj = self.model('ir.module.module')
        module_ids = module_obj.search([('name', '=', 'account_accountant')])
        module = module_obj.read(module_ids[0])

        self.assertFalse(module['state'] == 'installed', "Module account_accountant déjà installé")
        module_obj.button_immediate_install([module_ids[0]])

        module = module_obj.read(module_ids[0])
        self.assertTrue(module['state'] == 'installed', "Module account_accountant non installé")

    
    def test_040_install_l10n_be_module(self):
        """
        Install l10n_be module straight (don't use the installer)
        """
        self.login('admin', self.admin_password)
        module_obj = self.model('ir.module.module')
        module_ids = module_obj.search([('name', '=', 'l10n_be_davidts')])
        module = module_obj.read(module_ids[0])
 
        self.assertFalse(module['state'] == 'installed', "Module l10n_be déjà installé")
        module_obj.button_immediate_install([module_ids[0]])
 
        module = module_obj.read(module_ids[0])
        self.assertTrue(module['state'] == 'installed', "Module l10n_be non installé")

#     def test_045_install_l10n_be_davidts_module(self):
#         """
#         Install l10n_be module straight (don't use the installer)
#         """
#         self.login('admin', self.admin_password)
#         module_obj = self.model('ir.module.module')
#         module_ids = module_obj.search([('name', '=', 'l10n_be_davidts')])
#         module = module_obj.read(module_ids[0])
# 
#         self.assertFalse(module['state'] == 'installed', "Module l10n_be déjà installé")
#         module_obj.button_immediate_install([module_ids[0]])
# 
#         module = module_obj.read(module_ids[0])
#         self.assertTrue(module['state'] == 'installed', "Module l10n_be non installé")

    def test_050_configure_accounting(self):
        """
        Configure accounting via account.config.settings
        """
        self.login('admin', self.admin_password)
 
        config_obj = self.model('account.config.settings')
        # l10n_be_pcg_chart_template must be installed before we run this
        company_id = self.ref('res.company', 'base', 'main_company')
        chart_id = self.ref('account.chart.template', 'l10n_be_davidts', 'l10nbe_chart_template')
        eur_id = self.ref('res.currency', 'base', 'EUR')
 
        #
        # step 0 : On init le wizard
        new_config_values = {
            'company_id': company_id,
            'chart_template_id': chart_id,
            'code_digits': 6,
            'date_start': '2013-01-01',
            'date_stop': '2013-12-31',
            'period': 'month',
            'currency_id': eur_id,
        }
        config_id = config_obj.create(new_config_values)
 
        config_values = {
            'chart_template_id': chart_id,
            'code_digits': 6,
            'date_start': '2013-01-01',
            'date_stop': '2013-12-31',
            'period': 'month',
            'currency_id': eur_id,
        }
 
        #
        # step 1 : Sélection du Plan Comptable France
#        onchange_values = config_obj.onchange_chart_template_id([config_id], chart_id)
#        config_values.update(onchange_values['value'])
#        res = config_obj.write([config_id], config_values)
#        self.assertTrue(res, "chart of account install failed")
        try:
            config_obj.set_chart_of_accounts([config_id])
        except Fault as ex:
            if ex.faultCode.startswith("cannot marshal None unless allow_none is enabled"):
                print 'catch and ignore "{0}"'.format(ex.faultCode)
            else:
                raise Exception(ex.faultCode)
 
        #
        # step 2 : Création des périodes
        try:
            config_obj.set_fiscalyear([config_id])
        except Fault as ex:
            if ex.faultCode.startswith("cannot marshal None unless allow_none is enabled"):
                print 'catch and ignore "{0}"'.format(ex.faultCode)
            else:
                raise Exception(ex.faultCode)

    def test_100_install_module_core(self):
        """Core Module Installation"""
        self.login('admin', self.admin_password)
        module_obj = self.model('ir.module.module')
        module_ids = module_obj.search([('name', '=', self.core_module_name)])
        module = module_obj.read(module_ids[0])
 
        self.assertFalse(module['state'] == 'installed', "Core module already installed")
        module_obj.button_immediate_install([module_ids[0]])
 
        module = module_obj.read(module_ids[0])
        self.assertTrue(module['state'] == 'installed', "Core module install failed")
 
    def test_110_install_module_tests(self):
        """Test Module Installation"""
        self.login('admin', self.admin_password)
        module_obj = self.model('ir.module.module')
        module_ids = module_obj.search([('name', '=', self.test_module_name)])
        module = module_obj.read(module_ids[0])
 
        self.assertFalse(module['state'] == 'installed', "%s module already installed" % self.test_module_name)
        module_obj.button_immediate_install([module_ids[0]])
 
        module = module_obj.read(module_ids[0])
        self.assertTrue(module['state'] == 'installed', "%s module installation failed" % self.test_module_name)
 
 
    def test_200_install_module_base_data(self):
        """Base Data Installation"""
        if self.base_data_module_name:
            self.login('admin', self.admin_password)
            module_obj = self.model('ir.module.module')
            module_ids = module_obj.search([('name', '=', self.base_data_module_name)])
            self.assertTrue(len(module_ids) > 0, "base_data module does not exist")
            module = module_obj.read(module_ids[0])
 
            self.assertFalse(module['state'] == 'installed', "%s module already installed" % self.base_data_module_name)
            module_obj.button_immediate_install([module_ids[0]])
 
            module = module_obj.read(module_ids[0])
            self.assertTrue(module['state'] == 'installed', "%s module installation failed" % self.base_data_module_name)
 
    def test_300_adjust_translations(self):
        """We remove openerp translation for crm stages"""
        self.login('admin', self.admin_password)
        translation_obj = self.model('ir.translation')
        translation_ids = translation_obj.search([
            ('name', '=', 'crm.case.stage,name'),
            ('value', 'in', ('Proposition', 'Gagné',))
        ])
        self.assertTrue(len(translation_ids) == 2, "Failed to find openerp original translation for crm stages")
 
        result = translation_obj.unlink(translation_ids)
        self.assertTrue(result, "Failed to delete openerp original translation for crm stages")
 
    def test_120_configure_sales(self):
        """Configure various sales options"""
 
        self.login('admin', self.admin_password)
        config_obj = self.model('sale.config.settings')
 
        #company_id = self.ref('res.company', 'base', 'main_company')
 
        #
        # step 0 : On init le wizard
        new_config_values = {
 
            'group_sale_delivery_address': True, #Allow a different address for delivery and invoicing
            'module_order_mode_line':True, 
            'group_sale_pricelist':True,
            'group_invoice_deli_orders': True,
        }
        config_id = config_obj.create(new_config_values)
        config_obj.execute([config_id])
 
 
    def test_140_configure_stock_options(self):
        """Configure Stock options"""
 
        self.login('admin', self.admin_password)
        config_obj = self.model('stock.config.settings')
 
        # step 0 : On init le wizard
        new_config_values = {
            'group_stock_packaging': True, #Allow to define several packaging methods on products
        }
        config_id = config_obj.create(new_config_values)
        config_obj.execute([config_id])
 
    def test_150_configure_accounting(self):
        """Configure various accounting options"""
 
        self.login('admin', self.admin_password)
        tax_obj = self.model('account.tax.template')
 
        tax_ids = tax_obj.search([
            ('description', 'in', ('VAT-OUT-21-S', 'VAT-OUT-21-L', 'VAT-OUT-12-S', 'VAT-OUT-12-L',))
        ])
        self.assertTrue(len(tax_ids) == 4, "Tax configuration Failed ( unexpected tax object count )")
 
        new_tax_values = {
            'price_include': True,
        }
        result = tax_obj.write(tax_ids, new_tax_values)
        self.assertTrue(result, "Tax configuration Failed ( unable to set Tax included in price field)")
#begin Evolution #45137
    def test_160_config_settings(self):
        """Configure General configuration settings"""
        self.login('admin', self.admin_password)
        config_obj = self.model('base.config.settings')
        new_config_values = {
 
            'module_base_import': True, #Allow users to import data from CSV files
        }
        config_id = config_obj.create(new_config_values)
        config_obj.execute([config_id])
    def test_170_purchase_settings(self):
        """Configure purchase settings"""
        self.login('admin', self.admin_password)
        config_obj = self.model('purchase.config.settings')
        new_config_values = {
 
            'group_purchase_pricelist': True, #Allow users to import data from CSV files
        }
        config_id = config_obj.create(new_config_values)
        config_obj.execute([config_id])
# end Evolution #45137    
#settrace('localhost', port=20000, stdoutToServer=True, stderrToServer=True)