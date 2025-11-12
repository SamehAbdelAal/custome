
# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quality Base factory',
    'version': '1.0',
    'category': 'Manufacturing/Quality',
    'sequence': 50,
    'summary': 'Basic Feature for Quality',
    'depends': ['stock'],
    'description': """
Quality Base
===============
* Define quality points that will generate quality checks on pickings,
""",
    'data': [
        'security/quality.xml',
        'security/ir.model.access.csv',
        'data/mail_alias_data.xml',
        'data/quality_data.xml',
        'views/quality_views.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'quality/static/src/**/*',
        ],
        'web.qunit_suite_tests': [
            'quality/static/tests/*.js',
        ],
    }
}
