# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Accounting Factory',
    'version': '1.1',
    'category': 'Accounting/Accounting',
    'author': "Sameh Abdl-Aal",
    'sequence': 1,
    'summary': 'Enhanced Accounting Features for Odoo 18',
    'description': """
  This module extends and enhances the core Accounting functionalities in Odoo 18 Enterprise. 
It provides improved financial management tools, advanced journal handling, automated 
entries, reconciliation enhancements, better reporting structure, and seamless integration 
with invoicing, payments, banking, and analytic accounting. 

Designed to support enterprise-level financial operations, the module ensures accuracy, 
efficiency, and full compliance with Odoo's accounting workflow. Ideal for companies needing 
custom workflows, additional fields, or extended logic on Odoo’s native accounting system.

""",
    'website': 'https://sameh-abdlal.vercel.app/home',
    'depends': ['account'],
    'data': [
        'data/account_accountant_data.xml',
        'security/accounting_security.xml',
        'views/res_config_settings.xml',
        'views/partner_views.xml',
    ],
    'demo': ['demo/account_accountant_demo.xml'],
    'installable': True,
    'application': True,
    'license': 'OEEL-1',
    'images': ['static/description/icon.png'],
    'assets': {
        'web.assets_backend': [
            'accountant/static/src/js/tours/accountant.js',
        ],
        'web.assets_tests': [
            'accountant/static/tests/tours/*',
        ],
    }
}
