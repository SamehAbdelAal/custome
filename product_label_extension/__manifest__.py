# -*- coding: utf-8 -*-
{
    'name': 'Product Label Extension',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Extends product template with label printing fields',
    'description': """
        This module extends the product.template model with additional fields
        for label printing and production specifications including:
        - Product sequence ID
        - Material, Colors, Size specifications
        - Lamination, Varnish options
        - Roll and printing specifications
        - Customer linking
    """,
    'author': 'Sameh Abdel ael ',
    'website': '',
    'depends': ['product', 'sale', 'sale_management', 'mrp', 'quality_control'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/quality_check_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
