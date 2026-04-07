# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    color_fastness = fields.Boolean(
        string='Color Fastness',
        default=False,
        help='Check if the color fastness is acceptable'
    )
    cellophane_stability = fields.Boolean(
        string='Cellophane Stability',
        default=False,
        help='Check if the cellophane stability is acceptable'
    )
    support_undamaged = fields.Boolean(
        string='Support Undamaged',
        default=False,
        help='Check if the support is undamaged'
    )


class QualityCheckWizard(models.TransientModel):
    _inherit = 'quality.check.wizard'

    color_fastness = fields.Boolean(
        related='current_check_id.color_fastness',
        readonly=False
    )
    cellophane_stability = fields.Boolean(
        related='current_check_id.cellophane_stability',
        readonly=False
    )
    support_undamaged = fields.Boolean(
        related='current_check_id.support_undamaged',
        readonly=False
    )

    def do_pass(self):
        """Override to validate that all quality check fields are checked before passing."""
        missing_checks = []
        if not self.color_fastness:
            missing_checks.append(_('Color Fastness'))
        if not self.cellophane_stability:
            missing_checks.append(_('Cellophane Stability'))
        if not self.support_undamaged:
            missing_checks.append(_('Support Undamaged'))

        if missing_checks:
            raise UserError(
                _('Please check all required fields before passing:\n- %s') % '\n- '.join(missing_checks)
            )
        return super().do_pass()
