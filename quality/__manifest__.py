
# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quality factory',
    'version': '1.0',
    'category': 'Manufacturing/Quality',
    'sequence': 2,
    'author': "Sameh Abdl-Aal",
    'summary': 'Developed specifically for the factory of Engineer Sameh Abdel-Aal',
    'website': 'https://sameh-abdlal.vercel.app/home',
    'depends': ['stock'],
    'images': ['static/description/icon.png'],
    'description': """
 This module delivers an advanced extension of Odoo 18 Enterprise Accounting, introducing 
a robust set of financial enhancements designed for professional and high-volume business 
environments. It improves journal management, financial controls, automated bookkeeping, 
and reconciliation workflows while ensuring seamless integration with invoices, payments, 
banking operations, tax management, and analytic accounting.

With extended customization points and optimized performance, the module empowers 
organizations to adapt Odoo’s accounting engine to meet complex financial requirements, 
enhance accuracy, and streamline day-to-day financial operations. Ideal for enterprises 
seeking deeper financial visibility, compliance, and fully automated financial processes.

""",
    'data': [
        'security/quality.xml',
        'security/ir.model.access.csv',
        'data/mail_alias_data.xml',
        'data/quality_data.xml',
        'views/quality_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'quality/static/src/**/*',
        ],
        'web.qunit_suite_tests': [
            'quality/static/tests/*.js',
        ],
    }
}
