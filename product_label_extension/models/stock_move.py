# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    width_cm = fields.Float(string='Width (cm)')
    length_m = fields.Float(string='Length (m)')
    number_qty = fields.Float(string='Number')
    demand_computed = fields.Float(
        string='Demand Computed',
        compute='_compute_demand',
        store=True,
    )

    @api.depends('width_cm', 'length_m', 'number_qty')
    def _compute_demand(self):
        for rec in self:
            rec.demand_computed = (rec.width_cm / 100) * rec.length_m * rec.number_qty
