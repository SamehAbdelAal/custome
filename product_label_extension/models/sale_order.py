# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    LABEL_REQUIRED_FIELDS = [
        ('label_customer_id', 'Customer'),
        ('basic_colors', 'Basic Colors'),
        ('special_colors', 'Special Colors'),
        ('size_width_mm', 'Size (Width mm)'),
        ('size_height_mm', 'Size (Height mm)'),
        ('foil_type', 'Foil'),
        ('lamination', 'Lamination'),
        ('varnish', 'Varnish'),
        ('quantity_in_roll', 'Quantity in Roll'),
        ('core_size', 'Core Size'),
        ('winding_direction', 'Winding Direction'),
        ('gap_across_mm', 'Gap Across (mm)'),
        ('gap_around_mm', 'Gap Around (mm)'),
        ('image_across', 'Image Across'),
        ('image_around', 'Image Around'),
        ('no_of_abs', 'No Of Abs'),
        ('cylinder_no', 'Cylinder No'),
        ('material_id', 'Material'),
    ]

    def action_confirm(self):
        for order in self:
            for line in order.order_line:
                product_tmpl = line.product_template_id
                if not product_tmpl or product_tmpl.finsh_product:
                    continue
                missing = []
                for field_name, field_label in self.LABEL_REQUIRED_FIELDS:
                    if not product_tmpl[field_name]:
                        missing.append(field_label)
                if missing:
                    raise ValidationError(_(
                        "Product '%(product)s' is missing the following label specifications:\n%(fields)s\n\n"
                        "Please fill all label specification fields before confirming the sale order.",
                        product=product_tmpl.name,
                        fields=', '.join(missing),
                    ))
        return super().action_confirm()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    label_product_id = fields.Char(
        related='product_template_id.label_product_id', string='Product ID', readonly=True)
    label_customer_id = fields.Many2one(
        related='product_template_id.label_customer_id', string='Label Customer', readonly=True)
    basic_colors = fields.Selection(
        related='product_template_id.basic_colors', string='Basic Colors', readonly=True)
    special_colors = fields.Char(
        related='product_template_id.special_colors', string='Special Colors', readonly=True)
    size_width_mm = fields.Char(
        related='product_template_id.size_width_mm', string='Width (mm)', readonly=True)
    size_height_mm = fields.Char(
        related='product_template_id.size_height_mm', string='Height (mm)', readonly=True)
    foil_type = fields.Selection(
        related='product_template_id.foil_type', string='Foil', readonly=True)
    lamination = fields.Selection(
        related='product_template_id.lamination', string='Lamination', readonly=True)
    thickness = fields.Selection(
        related='product_template_id.thickness', string='Thickness', readonly=True)
    varnish = fields.Selection(
        related='product_template_id.varnish', string='Varnish', readonly=True)
    quantity_in_roll = fields.Char(
        related='product_template_id.quantity_in_roll', string='Qty in Roll', readonly=True)
    core_size = fields.Char(
        related='product_template_id.core_size', string='Core Size', readonly=True)
    winding_direction = fields.Selection(
        related='product_template_id.winding_direction', string='Winding Dir.', readonly=True)
    gap_across_mm = fields.Char(
        related='product_template_id.gap_across_mm', string='Gap Across (mm)', readonly=True)
    gap_around_mm = fields.Char(
        related='product_template_id.gap_around_mm', string='Gap Around (mm)', readonly=True)
    image_across = fields.Char(
        related='product_template_id.image_across', string='Image Across', readonly=True)
    image_around = fields.Char(
        related='product_template_id.image_around', string='Image Around', readonly=True)
    no_of_abs = fields.Char(
        related='product_template_id.no_of_abs', string='No Of Abs', readonly=True)
    cylinder_no = fields.Char(
        related='product_template_id.cylinder_no', string='Cylinder No', readonly=True)
    perforation = fields.Boolean(
        related='product_template_id.perforation', string='Perforation', readonly=True)
    invisible_ink = fields.Boolean(
        related='product_template_id.invisible_ink', string='Invisible Ink', readonly=True)
    back_side_print = fields.Boolean(
        related='product_template_id.back_side_print', string='Back Side Print', readonly=True)
    material_id = fields.Many2one(
        related='product_template_id.material_id', string='Material', readonly=True)
    calculated_width = fields.Integer(
        related='product_template_id.calculated_width', string='Calc. Width', readonly=True)
    length_quantity_in_meter = fields.Integer(
        related='product_template_id.length_quantity_in_meter', string='Length (m)', readonly=True)
