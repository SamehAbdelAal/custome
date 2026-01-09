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
    finsh_product = fields.Boolean(string='Raw Material', default=False)
    purchase_ok = fields.Boolean(default=False)
    sale_ok = fields.Boolean(default=True)

    @api.onchange('finsh_product')
    def change_sale_and_purchase_ok(self):
        for rec in self:
            if rec.finsh_product == False:
                rec.purchase_ok = False
                rec.sale_ok = True
            else:
                rec.purchase_ok = True
                rec.sale_ok = False

    viewable = fields.Boolean(default=True)
    selected_variant_id = fields.Many2one(
        'product.product',
        string='Matched Variant',
        help='Variant selected based on calculated width'
    )

    # 3. Material - Selection (Subject)
    material_id = fields.Many2one('product.template', string='Material')
    attribute_id = fields.Many2one(
        'product.product',
        string='Product Rules',
        compute='_compute_attribute_id',
        store=True,
    )

    def _safe_int(self, value):
        """Convert string value to int, return 0 if empty or invalid."""
        if not value:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    # Width Calculation
    @api.depends('no_of_abs', 'size_width_mm', 'gap_across_mm', 'size_height_mm', 'winding_direction')
    def _compute_calculated_width(self):
        for record in self:
            no_of_abs = record._safe_int(record.no_of_abs)
            size_width_mm = record._safe_int(record.size_width_mm)
            size_height_mm = record._safe_int(record.size_height_mm)
            gap_across_mm = record._safe_int(record.gap_across_mm)

            if record.winding_direction in ('0', '1', '2', '5', '6'):
                # Calculate using size_width_mm
                if no_of_abs and size_width_mm:
                    record.calculated_width = math.ceil(
                        no_of_abs * size_width_mm
                        + (no_of_abs - 1) * gap_across_mm
                        + 16
                    )
                else:
                    record.calculated_width = 0
            elif record.winding_direction in ('3', '4', '7', '8'):
                # Calculate using size_height_mm
                if no_of_abs and size_height_mm:
                    record.calculated_width = math.ceil(
                        no_of_abs * size_height_mm
                        + (no_of_abs - 1) * gap_across_mm
                        + 16
                    )
                else:
                    record.calculated_width = 0
            else:
                record.calculated_width = 0

    @api.depends('calculated_width', 'material_id')
    def _compute_attribute_id(self):
        """Update attribute_id based on calculated width from material_id."""
        for rec in self:
            if not rec.material_id or not rec.calculated_width:
                rec.attribute_id = False
                rec.viewable = True
                continue
            # Search for all variants in material_id
            all_variants = self.env['product.product'].search([
                ('product_tmpl_id', '=', rec.material_id.id),
            ])
            # Filter variants where attribute value >= calculated_width (numeric comparison)
            matching_variant = False
            for variant in all_variants:
                for attr_value in variant.product_template_attribute_value_ids:
                    try:
                        attr_num = float(attr_value.name)
                        if attr_num >= rec.calculated_width:
                            matching_variant = variant
                            break
                    except (ValueError, TypeError):
                        continue
                if matching_variant:
                    break
            if matching_variant:
                rec.attribute_id = matching_variant
                rec.viewable = False
            else:
                rec.attribute_id = False
                rec.viewable = True

    def _create_bom_for_product(self):
        """Create BOM for the product if conditions are met.
        Note: This must NOT be called from @api.onchange because record.id
        is a NewId (not a real DB id) until the record is saved.
        """
        for record in self:
            if not record.material_id:
                continue
            # Use attribute_id (Product Rules) if available, otherwise fall back to first variant
            material_product = record.attribute_id or record.material_id.product_variant_id
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
    basic_colors = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ], string='Basic Colors', help='Number of basic colors used in the product')

    # 5. Special Colors
    special_colors = fields.Char(string='Special Colors', help='Number of special colors used in the product')

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
            no_of_abs = record._safe_int(record.no_of_abs)
            if not no_of_abs:
                record.length_quantity_in_meter = 0
                continue

            gap_around = record._safe_int(record.gap_around_mm)
            basic_colors = record._safe_int(record.basic_colors)
            special_colors = record._safe_int(record.special_colors)
            size_height_mm = record._safe_int(record.size_height_mm)
            size_width_mm = record._safe_int(record.size_width_mm)

            # Calculate base_length based on winding direction
            if record.winding_direction in ('0', '1', '2', '5', '6'):
                if not size_height_mm:
                    record.length_quantity_in_meter = 0
                    continue
                base_length = (1000 * size_height_mm) / no_of_abs
            elif record.winding_direction in ('3', '4', '7', '8'):
                if not size_width_mm:
                    record.length_quantity_in_meter = 0
                    continue
                base_length = (1000 * size_width_mm) / no_of_abs
            else:
                record.length_quantity_in_meter = 0
                continue

            # Calculate gaps length between labels
            gaps_length = (math.ceil(1000 / no_of_abs) - 1) * gap_around
            # Save Label length and Color length separately
            labels_length = (base_length + gaps_length) / 1000
            colors_length = (basic_colors + special_colors) * 25
            # Calculate the length for 1000 labels
            length = labels_length + colors_length

            record.length_quantity_in_meter = int(math.ceil(length))

    # 6. Size (Width mm)
    size_width_mm = fields.Char(
        string='Size (Width mm)',
        help='Width of the product in millimeters'
    )

    # 7. Size (Height mm)
    size_height_mm = fields.Char(
        string='Size (Height mm)',
        help='Height of the product in millimeters'
    )

    # 8. Foil Type - Multiple choice
    foil_type = fields.Selection([
        ('no', 'No'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('other', 'Other (Enter the required option)'),
    ], string='Foil', default='no', help='Foil type for the product', oldname='mark_type')

    foil_type_other = fields.Char(
        string='Foil Type (Other)',
        help='Specify other foil type if selected',
        oldname='mark_type_other'
    )

    # 9. Lamination - Selection
    lamination = fields.Selection([
        ('no', 'No'),
        ('gloss', 'Gloss'),
        ('matte', 'Matte'),
    ], string='Lamination', default='no', help='Lamination type')
    thickness = fields.Selection([
        ('microns 35', 'Microns 35'),
        ('microns 20', 'Microns 20'),
        ('microns 18', 'Microns 18'),
        ('microns 15', 'Microns 15'),
        ('microns 10', 'Microns 10'),
    ], string='Thickness', help='Thickness in microns')
    open_microns = fields.Boolean(default=True)

    @api.onchange('lamination')
    def lamination_change(self):
        for rec in self:
            if rec.lamination == 'gloss' or rec.lamination == 'matte':
                rec.open_microns = False
            else:
                rec.open_microns = True

    # 10. Varnish - Selection
    varnish = fields.Selection([
        ('no', 'No'),
        ('gloss', 'Gloss'),
        ('matte', 'Matte'),
        ('raised', 'Raised'),
        ('spot', 'Spot'),
        ('sport', 'Sport'),
    ], string='Varnish', default='no', help='Varnish type')

    # 11. Quantity in Roll - Number (mandatory)
    quantity_in_roll = fields.Char(
        string='Quantity in Roll',
        help='Quantity of labels in one roll'
    )

    # 12. Core Size
    core_size = fields.Char(
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
    ], string='Winding Direction', help='Direction of label winding on roll')

    # 15. Gap Across (in millimeters)
    gap_across_mm = fields.Char(
        string='Gap Across (mm)',
        help='Gap across in millimeters'
    )

    # 16. Gap Around (in millimeters)
    gap_around_mm = fields.Char(
        string='Gap Around (mm)',
        help='Gap around in millimeters'
    )

    # 17. Image Across
    image_across = fields.Char(
        string='Image Across',
        help='Number of images across'
    )

    # 18. Image Around
    image_around = fields.Char(
        string='Image Around',
        help='Number of images around'

    )

    # 19. No Of Abs
    no_of_abs = fields.Char(
        string='No Of Abs',
        help='Number of absorptions'
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
        """Validate that a matching variant exists in material_id with attribute value >= calculated_width."""
        for record in self:
            if not record.material_id or not record.calculated_width:
                continue
            # Search for all variants in material_id
            all_variants = self.env['product.product'].search([
                ('product_tmpl_id', '=', record.material_id.id),
            ])
            # Check if any variant has attribute value >= calculated_width
            matching_variant = False
            for variant in all_variants:
                for attr_value in variant.product_template_attribute_value_ids:
                    try:
                        attr_num = float(attr_value.name)
                        if attr_num >= record.calculated_width:
                            matching_variant = True
                            break
                    except (ValueError, TypeError):
                        continue
                if matching_variant:
                    break
            if not matching_variant:
                raise ValidationError(
                    f"No variant found in material '{record.material_id.name}' with width >= '{record.calculated_width}'. "
                    "Please ensure the material has a variant with a matching or larger width attribute."
                )


class inheritpiiofmattrile(models.Model):
    _inherit = 'mrp.bom'
    color_length = fields.Char(string='color length ')
    labels_length = fields.Char(string='label length ')
