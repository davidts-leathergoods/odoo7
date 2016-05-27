# coding: utf8
{
    'name': 'Audaxis Memory Analyzer',
    'version': '0.1',
    'category': 'Audaxis Dev Tools',
    'author': 'Cyril MORISSE - @cmorisse',
    'description': """This module produce various statistics about memory usage. It consists in a schedule
     action which dumps (every x miuntes) memory usage information about:
      - osv_memory objects
      - objects collected, unreachable ... TO COMPLETE

    This module main goal is to provide some concrete help in debugging odoo memory leaks especially
    those related to osv objects.""",
    'complexity': 'expert',
    'website': 'http://twitter.com/cmorisse',
    'depends': [],
    'data': [
        'data/ir_config_parameter.xml',
        'data/ax_memory_analyzer_process.xml',
        'wizards/ax_memory_analyzer_wizard.xml',
        'config/memory_analyzer_config_view.xml'
    ],
    'test': [],
    'application': True,
    'auto_install': False,
    'installable': True,
}
