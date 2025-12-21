# -*- coding: utf-8 -*-
import logging
import math
from email.policy import default
from time import sleep

from odoo import models, fields, api, Command
from odoo.exceptions import ValidationError, UserError

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
    material_id = fields.Many2one('product.template', string='Material',ondelete='set null',required=False)
    attribute_id = fields.Many2one(
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
                  + (record.no_of_abs - 1) * record.gap_across_mm
                  + 16
                ) / 10
            else:
                record.calculated_width = 0.0

    @api.depends('calculated_width','attribute_line_ids')
    def _compute_attribute_id(self):
        """Update attribute_id based on calculated width."""
        # Find attribute values matching the calculated width
        for rec in self:
            matching_values = rec.attribute_line_ids.value_ids.filtered(
                lambda x: x.name == str(rec.calculated_width)
            )
            if matching_values:
                # Find the product variant that has this attribute value
                matching_variant = self.env['product.product'].search([
                    ('product_tmpl_id', '=', rec._origin.id),
                    ('product_template_attribute_value_ids.name', '=', str(rec.calculated_width))
                ], limit=1)
                self.attribute_id = matching_variant or False
                self.viewable = False
            else:
                self.attribute_id = False
                self.viewable = True

    def _create_bom_for_product(self):
        """Create BOM for the product if conditions are met."""
        for record in self:
            if not record.attribute_id:
                continue
            if not record.material_id:
                continue
            self.env['mrp.bom'].sudo().create({
                'product_tmpl_id': record.id,
                'product_qty': 1000,
                'product_uom_id': record.uom_id.id,
                'bom_line_ids': [
                    Command.create({
                        'product_id': record.material_id.id,
                        'product_qty': record.length_quantity_in_meter or 1.0,
                    }),
                ],
            })
    # Calculated Width - Computed field
    calculated_width = fields.Integer(
        string='Calculated Width',
        compute='_compute_calculated_width',
        store=True,
        help='Calculated width based on: (no_of_abs * size_width_mm) + ((no_of_abs - 1) * gap_across_mm) + 1.6'
    )

    # 4. Basic Colors
    basic_colors = fields.Integer(
        string='Basic Colors',
        default=0,
        help='Number of basic colors used in the product'
    )

    # 5. Special Colors
    special_colors = fields.Integer(
        string='Special Colors',
        default=0,
        help='Number of special colors used in the product'
    )

    # Length Quantity in meter - Computed field
    length_quantity_in_meter = fields.Float(
        string='Length Quantity (m)',
        compute='_compute_length_quantity_in_meter',
        store=True,
        help='Calculated length quantity in meters based on winding direction'
    )

    @api.depends('winding_direction', 'size_height_mm', 'size_width_mm', 'no_of_abs', 'gap_around_mm', 'basic_colors', 'special_colors')
    def _compute_length_quantity_in_meter(self):
        """
        Calculate Length Quantity in meter based on winding direction:
        IF Winding Direction = 0 or 1 or 2 or 5 or 6:
            Length = ((2000 * Height / NoOfAbs) + (ceil(2000 / NoOfAbs) - 1) * GapAround) / 1000 + (BasicColors + SpecialColors) * 150
        ELSE IF Winding Direction = 3 or 4 or 7 or 8:
            Length = ((2000 * Width / NoOfAbs) + (ceil(2000 / NoOfAbs) - 1) * GapAround) / 1000 + (BasicColors + SpecialColors) * 150
        """
        for record in self:
            if not record.no_of_abs or record.no_of_abs == 0:
                record.length_quantity_in_meter = 0.0
                return
            no_of_abs = record.no_of_abs
            gap_around = record.gap_around_mm or 0.0
            basic_colors = record.basic_colors or 0
            special_colors = record.special_colors or 0

            # Common part of the formula
            ceil_part = (math.ceil(2000 / no_of_abs) - 1) * gap_around
            color_part = (basic_colors + special_colors) * 150

            # Check winding direction
            if record.winding_direction in ('0', '1', '2', '5', '6'):
                # Use Height
                height = record.size_height_mm or 0.0
                length = ((2000 * height / no_of_abs) + ceil_part) / 1000 + color_part
            elif record.winding_direction in ('3', '4', '7', '8'):
                # Use Width
                width = record.size_width_mm or 0.0
                length = ((2000 * width / no_of_abs) + ceil_part) / 1000 + color_part
            else:
                length = 0.0

            record.length_quantity_in_meter = length

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
        ('0', 'Direction 0'),
        ('1', 'Direction 1 - Labels come off roll facing up'),
        ('2', 'Direction 2 - Labels come off roll facing down'),
        ('3', 'Direction 3 - Labels wind clockwise'),
        ('4', 'Direction 4 - Labels wind counter-clockwise'),
        ('5', 'Direction 5'),
        ('6', 'Direction 6'),
        ('7', 'Direction 7'),
        ('8', 'Direction 8'),
    ], string='Winding Direction', required=True,help='Direction of label winding on roll')

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
        records = super().create(vals_list)
        # Create BOM only on initial creation, not on updates
        records._create_bom_for_product()
        return records

    @api.constrains('get_up')
    def _check_get_up_range(self):
        for record in self:
            if record.get_up < 0 or record.get_up > 8:
                raise ValidationError(
                    'Get Up value must be between 0 and 8'
                )
    @api.constrains('get_up')
    def _check_get_up_range(self):
       if not self.material_id:
           raise ValidationError(
               'please selected material'
           )