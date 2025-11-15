# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mail factory',
    'category': 'Productivity/Discuss',
    'depends': ['mail'],
    'description': """
Bridge module for mail and factory
=====================================

Display a preview of the last 
""",
    'auto_install': False,
    'installable': True,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'mail_enterprise/static/src/core/common/**/*',
            'mail_enterprise/static/src/**/*',
        ],
        'web.assets_tests': [
            'mail_enterprise/static/tests/tours/**/*',
        ],
        'web.qunit_suite_tests': [
            'mail_enterprise/static/tests/**/*.js',
            ('remove', 'mail_enterprise/static/tests/tours/**/*'),
        ],
    }
}
