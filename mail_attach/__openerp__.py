#  -*- coding: utf-8 -*-

{
    "name": "Attach mail",
    "version": "0.1",
    "author": "Ibtissem Zeiri",
    "category": 'Audaxis',
    "description": """
        Attach object to mail
    """,
    'website': 'http://www.openerp.com',
    "depends": ["web", "base", "crm", "sale", "purchase",
              ],
    'data': [
             "wizard/mail_message_wizard.xml",
             "wizard/mail_compose_message.xml",

    ],
    'installable': True,
    'auto_install': False,
    'js': [
        'static/src/js/mail.js',
    ],
    'qweb': [
        'static/src/xml/mail.xml',
    ],
}
#  vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
