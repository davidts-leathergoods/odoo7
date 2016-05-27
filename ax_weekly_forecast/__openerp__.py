# coding: utf8
# TODO: Cmo,Reprendre tous les textes de licence dans les fichiers
{
    'name': 'Etat des stock par produit',
    'version': '0.1',
    'category': u"visualisation du stock prévisionnel ",
    'author': 'Audaxis general',
    'description': u"addons pour la visualisation du stock prévisionnel .",
    'complexity': 'expert',
    'depends': ['base', 'stock'],
    'data': [
        "security/ir.model.access.csv",
        "views/product_view.xml",
    ],
    'test': [],
    'application': True,
    'auto_install': False,
    'installable': True,
}
