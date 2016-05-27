# coding: utf8
{
    'name': 'Disable change rate conversion',
    'version': '0.1',
    'category': 'Audaxis Dev Tools',
    'author': 'Assem BAYAHI - tn.linkedin.com/in/bayahiassem/en',
    'description': """
     When creating an Order with a currency different of the company currency, odoo automatically
     calculate the price using the change rate, this module will give you the possibility, when creating a pricelist, to choose
     whether to apply or not the change rate. Example:
     Default currency: Euro
     Client currency: USD
     Change rate: 1.28
     Pricelist rule: price = price * 1.2
     Product P1: Unit Price = 3 Euro
     Quantity: 6

     * With rate conversion:
     Price = 6 * 3 * 1.28 * 1.2 = 27.648 $

     * Without conversion:
     Price = 6 * 3 * 1.2 = 21.6 $

     => We need this behaviour when we want to define explicitly the value of the product in a foreign currency.
     """,
    'complexity': 'expert',
    'website': 'tn.linkedin.com/in/bayahiassem/en',
    'depends': ['sale'],
    'data': [
        'views/product_pricelist_view.xml'
    ],
    'test': [],
    'application': True,
    'auto_install': False,
    'installable': True,
}