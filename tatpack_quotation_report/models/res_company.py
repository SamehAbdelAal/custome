# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Custom fields for TatPack footer
    head_office_address = fields.Text(
        string='Head Office Address',
        default='87, Pharaonic Company Blocks, Block No. 3, El Mariouteya - Faisal.',
        help='Head office address for report footer'
    )

    factory_address = fields.Text(
        string='Factory Address',
        default='Abu Rawash - El Mansourieh Haram Road, next to Star Water.',
        help='Factory address for report footer'
    )

    footer_phone_1 = fields.Char(
        string='Footer Phone 1',
        default='00235951307',
        help='First phone number for report footer'
    )

    footer_phone_2 = fields.Char(
        string='Footer Phone 2',
        default='01014077379',
        help='Second phone number for report footer'
    )
