# -*- coding: utf-8 -*-
import logging
from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # 1. Product ID - Sequence
    label_product_id = fields.Char(
        string='Product ID',
        readonly=True,
        copy=False,
        default='New',
        help='Unique product sequence ID'
    )
    viewable = fields.Boolean(default=True)
    selected_variant_id = fields.Many2one(
        'product.product',
        string='Matched Variant',
        help='Variant selected based on calculated width'
    )
    # 2. Product Name - Text
    label_product_name = fields.Char(
        string='Product Name',
        help='Product name for label'
    )


    # 3. Material - Selection (Subject)
    material_id = fields.Many2one('product.product', string='Material')
    attribute_id = fields.Many2many(
        'product.product',
        string='Product Rules',
        compute='_compute_attribute_id',
        store=True,
    )

    @api.depends('no_of_abs', 'size_width_mm', 'gap_across_mm')
    def _compute_calculated_width(self):
        for record in self:
            if record.no_of_abs and record.size_width_mm:
                record.calculated_width = (
                    record.no_of_abs * record.size_width_mm
                    + ((record.no_of_abs - 1) * (record.gap_across_mm + 16)) / 10
                )
            else:
                record.calculated_width = 0.0

    @api.depends('calculated_width')
    def _compute_attribute_id(self):
        """Update attribute_id based on calculated width."""
        for record in self:
            if record.calculated_width:
                matching_products = self.env['product.product']
                products = self.env['product.product'].search([])
                for p in products:
                    for v in p.product_template_variant_value_ids:
                        if v.name == str(int(record.calculated_width)):
                            matching_products |= p
                record.attribute_id = matching_products
                record.viewable = bool(not matching_products)
            else:
                record.attribute_id = False
                record.viewable = True
    # Calculated Width - Computed field
    calculated_width = fields.Integer(
        string='Calculated Width',
        compute='_compute_calculated_width',
        store=True,
        help='Calculated width based on: (no_of_abs * size_width_mm) + ((no_of_abs - 1) * gap_across_mm) + 1.6'
    )

    # 4. Basic Colors
    basic_colors = fields.Char(
        string='Basic Colors',
        help='Basic colors used in the product'
    )

    # 5. Special Colors
    special_colors = fields.Char(
        string='Special Colors',
        help='Special colors used in the product'
    )

    # 6. Size (Width mm)
    size_width_mm = fields.Float(
        string='Size (Width mm)',
        help='Width of the product in millimeters',
        default=0.0
    )

    # 7. Size (Height mm)
    size_height_mm = fields.Float(
        string='Size (Height mm)',
        help='Height of the product in millimeters'
    )

    # 8. Mark Type - Multiple choice
    mark_type = fields.Selection([
        ('no', 'No'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('other', 'Other (Enter the required option)'),
    ], string='Mark Type', default='no', help='Mark type for the product')

    mark_type_other = fields.Char(
        string='Mark Type (Other)',
        help='Specify other mark type if selected'
    )

    # 9. Lamination - Selection
    lamination = fields.Selection([
        ('no', 'No'),
        ('gloss', 'Gloss'),
        ('matte', 'Matte'),
    ], string='Lamination', default='no', help='Lamination type')

    # 10. Varnish - Selection
    varnish = fields.Selection([
        ('no', 'No'),
        ('gloss', 'Gloss'),
        ('matte', 'Matte'),
        ('raised', 'Raised'),
    ], string='Varnish', default='no', help='Varnish type')

    # 11. Quantity in Roll - Number (mandatory)
    quantity_in_roll = fields.Integer(
        string='Quantity in Roll',
        required=True,
        default=0,
        help='Quantity of labels in one roll'
    )

    # 12. Core Size
    core_size = fields.Float(
        string='Core Size',
        help='Core size of the roll'
    )

    # 13. Winding Direction
    winding_direction = fields.Selection([
        ('1', 'Direction 1 - Labels come off roll facing up'),
        ('2', 'Direction 2 - Labels come off roll facing down'),
        ('3', 'Direction 3 - Labels wind clockwise'),
        ('4', 'Direction 4 - Labels wind counter-clockwise'),
    ], string='Winding Direction', help='Direction of label winding on roll')

    # 14. Get Up (0 to 8)
    get_up = fields.Integer(
        string='Get Up',
        default=0,
        help='Get up value from 0 to 8'
    )

    # 15. Gap Across (in millimeters)
    gap_across_mm = fields.Float(
        string='Gap Across (mm)',
        help='Gap across in millimeters',
        default=0.0
    )

    # 16. Gap Around (in millimeters)
    gap_around_mm = fields.Float(
        string='Gap Around (mm)',
        help='Gap around in millimeters'
    )

    # 17. Image Across
    image_across = fields.Integer(
        string='Image Across',
        help='Number of images across'
    )

    # 18. Image Around
    image_around = fields.Integer(
        string='Image Around',
        help='Number of images around'
    )

    # 19. No Of Abs
    no_of_abs = fields.Integer(
        string='No Of Abs',
        help='Number of absorptions',
        default=0
    )

    # 20. Cylinder No
    cylinder_no = fields.Char(
        string='Cylinder No',
        help='Cylinder number'
    )

    # 21. Perforation - Yes/No
    perforation = fields.Boolean(
        string='Perforation',
        default=False,
        help='Whether perforation is required'
    )

    # 22. Invisible Ink - Yes/No
    invisible_ink = fields.Boolean(
        string='Invisible Ink',
        default=False,
        help='Whether invisible ink is used'
    )

    # 23. Back Side Print - Yes/No
    back_side_print = fields.Boolean(
        string='Back Side Print',
        default=False,
        help='Whether back side printing is required'
    )

    # 24. Customer - Linked to partner
    label_customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain=[('customer_rank', '>', 0)],
        help='Customer associated with this product specification'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('label_product_id', 'New') == 'New':
                vals['label_product_id'] = self.env['ir.sequence'].next_by_code(
                    'product.label.sequence') or 'New'
        return super().create(vals_list)

    @api.constrains('get_up')
    def _check_get_up_range(self):
        for record in self:
            if record.get_up < 0 or record.get_up > 8:
                raise ValidationError(
                    'Get Up value must be between 0 and 8'
                )
