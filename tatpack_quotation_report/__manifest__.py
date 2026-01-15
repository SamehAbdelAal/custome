# -*- coding: utf-8 -*-
{
    'name': 'TatPack Quotation Report',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Custom quotation report for TatPack with product label details',
    'description': """
        Custom quotation report for TatPack company featuring:
        - Custom header with company logo
        - Product description with label specifications
        - Terms and conditions of sale
        - Custom footer with company contact information
    """,
    'author': 'TatPack',
    'website': 'http://www.tatpack.com',
    'depends': ['sale', 'sale_management', 'product_label_extension'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/sale_order_views.xml',
        'report/tatpack_quotation_report.xml',
        # 'report/tatpack_quotation_template.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
