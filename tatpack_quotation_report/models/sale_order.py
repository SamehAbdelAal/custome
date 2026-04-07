# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Quotation Subject/Reference
    quotation_subject = fields.Char(
        string='Subject',
        help='Subject line for quotation (e.g., labels enquiry)'
    )

    # Terms and Conditions Fields
    delivery_terms = fields.Char(
        string='Delivery Terms',
        default='To be discussed.',
        help='Delivery terms for the quotation'
    )

    lead_time = fields.Char(
        string='Lead Time',
        default='To be discussed.',
        help='Lead time for production/delivery'
    )

    validity_days = fields.Char(
        string='Validity of Quotation',
        default='5 Days.',
        help='Number of days the quotation is valid'
    )

    payment_terms_text = fields.Char(
        string='Payment Terms Text',
        default='45 days from the date of receipt',
        help='Payment terms description'
    )

    tolerance_percentage = fields.Char(
        string='Tolerance Percentage',
        default='+/- 10%',
        help='Acceptable tolerance for order quantity'
    )

    # Closing Section
    closing_text = fields.Text(
        string='Closing Text',
        default='We hope the above offer meets with your expectations and look forward to receiving your further instructions.',
        help='Closing paragraph for the quotation'
    )

    # Signature Section
    signatory_company = fields.Char(
        string='For Company',
        default='TaTPack',
        help='Company name for signature section (e.g., For TaTPack)'
    )

    signatory_name = fields.Char(
        string='Signatory Name',
        default='Mahmoud Abdullah',
        help='Name of person signing the quotation'
    )

    signatory_mobile = fields.Char(
        string='Signatory Mobile',
        default='01000575130',
        help='Mobile number of signatory'
    )

    # Price includes tax or not
    prices_include_tax = fields.Boolean(
        string='Prices Include Tax',
        default=False,
        help='Check if prices include sales tax'
    )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Additional fields for label quotation
    no_of_variants = fields.Integer(
        string='No. of Variants',
        default=1,
        help='Number of product variants'
    )
