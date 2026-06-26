# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmsUnitOwner(models.Model):
    _name = 'pms.unit.owner'
    _description = 'Unit Owner – links an Owner to a Property/Unit'
    _order = 'start_date desc, id desc'

    # ── Relationships ───────────────────────────────────────────────────
    owner_id = fields.Many2one(
        'pms.owner',
        string='Owner',
        required=True,
        ondelete='restrict',
        index=True,
        help='The owner for the unit selected.',
    )
    unit_id = fields.Many2one(
        'pms.property',
        string='Unit / Property',
        required=True,
        ondelete='cascade',
        index=True,
        help='The unit the owner owns.',
    )
    contract_id = fields.Integer(
        string='Contract ID',
        required=True,
        help='The contract that is attached to the owner selected.',
    )

    # ── Contract Info ────────────────────────────────────────────────────
    tax_mode = fields.Selection(
        [
            ('inclusive', 'Inclusive'),
            ('exclusive', 'Exclusive'),
            ('none', 'None'),
        ],
        string='Tax Mode',
        required=True,
        default='exclusive',
    )

    # ── Dates ───────────────────────────────────────────────────────────
    start_date = fields.Date(
        string='Start Date',
        required=True,
        index=True,
    )
    end_date = fields.Date(
        string='End Date',
        index=True,
    )

    # ── Owner / Unit computed helpers ───────────────────────────────────
    owner_name = fields.Char(
        string='Owner Name',
        related='owner_id.name',
        store=True,
    )
    unit_name = fields.Char(
        string='Unit Name',
        related='unit_id.name',
        store=True,
    )

    # ── Constraints ────────────────────────────────────────────────────
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError(_('End date must be on or after the start date.'))