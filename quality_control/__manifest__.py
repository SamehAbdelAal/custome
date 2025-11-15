# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quality factory',
    'version': '1.0',
    'category': 'Manufacturing/Quality',
    'sequence': 120,
    'summary': 'Control the quality of your products',
    'website': 'https://sameh-abdlal.vercel.app/home',
    'depends': ['quality'],
    'description': """
Quality Control
===============
  Quality factory 
""",
    'data': [
        'data/quality_control_data.xml',
        'report/worksheet_custom_reports.xml',
        'report/worksheet_custom_report_templates.xml',
        'views/quality_views.xml',
        'views/product_views.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_lot_views.xml',
        'wizard/quality_check_wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'data/quality_control_demo.xml',
    ],
    'images': [
        'static/src/img/icon.png',
    ],
    'application': True,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'quality_control/static/src/**/*',
        ],
    }
}
