import shutil
import os

__author__ = 'cmorisse'
import openerp
import socket
import logging

_logger = logging.getLogger('Inouk Server Detector')


def colorize_menu():
    # if we want to show visual difference between differents servers Or if we are in production server we have to force
    # the original color

    server_type = 'production'

    if openerp.tools.config.options.get('ik_sd_colorise', None):
        server_type = openerp.ik_sd_server_kind

    base_path = os.path.dirname(os.path.realpath(__file__))

    css_to_copy_file = '%s/static/src/css/server_type_style_%s.css' % (base_path, server_type)
    original_css = '%s/static/src/css/server_type_style.css' % base_path

    _logger.info(' Use CSS: %s ' % css_to_copy_file)

    shutil.copyfile(css_to_copy_file, original_css)


# We will disable all configured crons
def disable_crons():
    disable_from_id = openerp.tools.config.options.get('ik_sd_cron_id', None)

    if disable_from_id:
        where = None
        # if we have in config something like '>8', we disable all crons with ID > 8
        if disable_from_id[0] == '>':
            where = disable_from_id
        else:
            # we have a list of ID or External IDs
            disable_ids = disable_from_id.split(',')

            if len(disable_ids) == 0:
                _logger.error("ik_sd_cron_id must contains a value like '>8' or like '8,5,9'")
            else:
                if disable_ids[0].isdigit():
                    # we have a list of IDS
                    where = " IN (%s)" % disable_from_id
                else:
                     # we have a list of external IDS
                    where = " IN (SELECT res_id FROM ir_model_data WHERE model='ir.cron' AND name IN (%s)) " % ','.join("'{0}'".format(w) for w in disable_ids)

        if where:
            registries = openerp.modules.registry.RegistryManager.registries
            for db_name, registry in registries.items():
                try:
                    db = openerp.sql_db.db_connect(db_name)
                    cr = db.cursor()

                    sql = "UPDATE ir_cron SET active=False WHERE id %s" % where
                    cr.execute(sql)
                    cr.commit()

                    _logger.info("Server is not Production, we desactivated crons with this request = %s" % sql)
                finally:
                    cr.close()


def server_detect():

    try:
        current_ip = socket.gethostbyname(socket.gethostname())
    except:
        current_ip = ''

    #in some case, this will return 127.* so we have to use another method
    if current_ip.startswith("127."):
        current_ip = [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

    if openerp.tools.config.options.get('ik_sd_staging_servers_ips', None):
        staging_servers_ips = openerp.tools.config.options['ik_sd_staging_servers_ips'].split(',')
    else:
        staging_servers_ips = []

    if openerp.tools.config.options.get('ik_sd_production_servers_ips', None):
        production_servers_ips = openerp.tools.config.options['ik_sd_production_servers_ips'].split(',')
    else:
        production_servers_ips = []

    if openerp.tools.config.options.get('ik_sd_email_debug_recipients', None):
        openerp.ik_sd_email_debug_recipients = openerp.tools.config.options['ik_sd_email_debug_recipients']
    else:
        openerp.ik_sd_email_debug_recipients = []

    if current_ip in staging_servers_ips:
        openerp.ik_sd_is_production_server = False
        openerp.ik_sd_is_staging_server = True
        openerp.ik_sd_is_test_server = False
        openerp.ik_sd_detected_ip = current_ip
        openerp.ik_sd_server_kind = 'staging'
        colorize_menu()
        disable_crons()
        _logger.info("Server is 'staging', detected IP address=%s" % current_ip)
        return

    if current_ip in production_servers_ips:
        openerp.ik_sd_is_production_server = True
        openerp.ik_sd_is_staging_server = False
        openerp.ik_sd_is_test_server = False
        openerp.ik_sd_detected_ip = current_ip
        openerp.ik_sd_server_kind = 'production'
        colorize_menu()
        _logger.info("Server is 'production', detected IP address=%s" % current_ip)
        return

    openerp.ik_sd_is_production_server = False
    openerp.ik_sd_is_staging_server = False
    openerp.ik_sd_is_test_server = True
    openerp.ik_sd_detected_ip = current_ip
    openerp.ik_sd_server_kind = 'test'
    colorize_menu()
    disable_crons()
    _logger.info("Server is 'test (or dev)', detected IP address=%s" % current_ip)
