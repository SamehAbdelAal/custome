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


    # 3. Material - Selection (Subject)
    material_id = fields.Many2one('product.template', string='Material',required=False)
    attribute_id = fields.Many2one(
        'product.product',
        string='Product Rules',
        compute='_compute_attribute_id',
        store=True,
    )

    @api.depends('no_of_abs', 'size_width_mm', 'gap_across_mm', 'size_height_mm', 'winding_direction')
    def _compute_calculated_width(self):
        for record in self:
            if record.winding_direction in ('0', '1', '2', '5', '6'):
                # Calculate using size_width_mm
                if record.no_of_abs and record.size_width_mm:
                    record.calculated_width = math.ceil((
                                    record.no_of_abs * record.size_width_mm
                                    + (record.no_of_abs - 1) * (record.gap_across_mm or 0)
                                    + 16
                            ) / 10)
                else:
                    record.calculated_width = 0
            elif record.winding_direction in ('3', '4', '7', '8'):
                # Calculate using size_height_mm
                if record.no_of_abs and record.size_height_mm:
                    record.calculated_width = math.ceil((
                                    record.no_of_abs * record.size_height_mm
                                    + (record.no_of_abs - 1) * (record.gap_across_mm or 0)
                                    + 16
                            ) / 10)
                else:
                    record.calculated_width = 0
            else:
                record.calculated_width = 0

    @api.depends('calculated_width', 'material_id')
    def _compute_attribute_id(self):
        """Update attribute_id based on calculated width from material_id."""
        for rec in self:
            if not rec.material_id:
                rec.attribute_id = False
                rec.viewable = True
                continue
            # Search for variant in material_id where product_template_attribute_value_ids.name == calculated_width
            matching_variant = self.env['product.product'].search([
                ('product_tmpl_id', '=', rec.material_id.id),
                ('product_template_attribute_value_ids.name', '=', str(rec.calculated_width))
            ], limit=1)
            print(matching_variant)
            if matching_variant:
                rec.attribute_id = matching_variant
                rec.viewable = False
            else:
                rec.attribute_id = False
                rec.viewable = True
                raise ValidationError(
                    f"No matching variant found in material '{rec.material_id.name}' "
                    f"with calculated width '{rec.calculated_width}'. "
                    "Please select a material that has a variant with this width attribute."
                )

    def _create_bom_for_product(self):
        """Create BOM for the product if conditions are met.
        Note: This must NOT be called from @api.onchange because record.id
        is a NewId (not a real DB id) until the record is saved.
        """
        for record in self:
            if not record.material_id:
                continue
            # Get the first product variant from the material template
            material_product = record.material_id.product_variant_id
            if not material_product:
                continue
            self.env['mrp.bom'].sudo().create({
                'product_tmpl_id': record.id,
                'product_qty': 1000,
                'product_uom_id': record.uom_id.id,
                'bom_line_ids': [
                    Command.create({
                        'product_id': material_product.id,
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
    length_quantity_in_meter = fields.Integer(
        string='Length Quantity (m)',
        compute='_compute_length_quantity_in_meter',
        store=True,
        help='Calculated length quantity in meters based on winding direction'
    )

    @api.depends(
        'winding_direction',
        'size_height_mm',
        'size_width_mm',
        'no_of_abs',
        'gap_around_mm',
        'basic_colors',
        'special_colors'
    )
    def _compute_length_quantity_in_meter(self):
        for record in self:
            if not record.no_of_abs:
                record.length_quantity_in_meter = 0
                continue

            no_of_abs = record.no_of_abs
            gap_around = record.gap_around_mm or 0.0
            basic_colors = record.basic_colors or 0
            special_colors = record.special_colors or 0

            ceil_part = (math.ceil(2000 / no_of_abs) - 1) * gap_around
            color_part = (basic_colors + special_colors) * 150

            if record.winding_direction in ('0', '1', '2', '5', '6'):
                base = (2000 * (record.size_height_mm or 0.0)) / no_of_abs
            elif record.winding_direction in ('3', '4', '7', '8'):
                base = (2000 * (record.size_width_mm or 0.0)) / no_of_abs
            else:
                record.length_quantity_in_meter = 0
                continue

            length = (base + ceil_part) / 1000 + color_part

            # 👇 الضمان النهائي
            record.length_quantity_in_meter = int(math.ceil(length))

    # 6. Size (Width mm)
    size_width_mm = fields.Integer(
        string='Size (Width mm)',
        help='Width of the product in millimeters',
        default=0.0
    )

    # 7. Size (Height mm)
    size_height_mm = fields.Integer(
        string='Size (Height mm)',
        help='Height of the product in millimeters'
    )

    # 8. Mark Type - Multiple choice
    mark_type = fields.Selection([
        ('no', 'No'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('other', 'Other (Enter the required option)'),
    ], string='Mark', default='no', help='Mark type for the product')

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
    microns = fields.Selection([
        ('microns 35', 'Microns 35'),
        ('microns 15', 'Microns 15'),
        ('microns 10', 'Microns 10'),
    ], string='Microns', help='Microns')
    open_microns =fields.Boolean(default=True)
    @api.onchange('lamination')
    def lamination_change(self):
        for rec in self:
            if rec.lamination == 'gloss' or  rec.lamination == 'matte':
                rec.open_microns = False
            else:
                rec.open_microns = True
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
    core_size = fields.Integer(
        string='Core Size',
        help='Core size of the roll'
    )

    # 13. Winding Direction
    winding_direction = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
    ], string='Winding Direction', required=True,help='Direction of label winding on roll')



    # 15. Gap Across (in millimeters)
    gap_across_mm = fields.Integer(
        string='Gap Across (mm)',
        help='Gap across in millimeters',
        default=0.0
    )

    # 16. Gap Around (in millimeters)
    gap_around_mm = fields.Integer(
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


    @api.constrains('material_id', 'calculated_width')
    def _check_material_variant_exists(self):
        """Validate that a matching variant exists in material_id for the calculated_width."""
        for record in self:
            if not record.material_id:
                continue
            # Check if a variant exists with matching attribute value
            matching_variant = self.env['product.product'].search([
                ('product_tmpl_id', '=', record.material_id.id),
                ('product_template_attribute_value_ids.name', '=', str(record.calculated_width))
            ], limit=1)
            if not matching_variant:
                raise ValidationError(
                    f"No variant found in material '{record.material_id.name}' with width '{record.calculated_width}'. "
                    "Please ensure the material has a variant with the matching calculated width attribute."
                )
