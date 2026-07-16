# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmsReservationCharge(models.Model):
    _name = 'pms.reservation.charge'
    _description = 'Property Reservation Charge'
    _order = 'transaction_date, id'

    reservation_id = fields.Many2one(
        'pms.booking',
        string='Reservation',
        required=True,
        ondelete='cascade',
        index=True,
    )
    charge_type_id = fields.Many2one(
        'pms.charge.type',
        string='Charge Type',
        required=True,
        ondelete='restrict',
        index=True,
    )
    description = fields.Char(
        string='Description',
    )
    quantity = fields.Float(
        string='Quantity',
        digits='Product Unit of Measure',
        default=1.0,
    )
    unit_amount = fields.Monetary(
        string='Unit Amount',
        currency_field='currency_id',
        required=True,
        default=0.0,
    )
    gross_amount = fields.Monetary(
        string='Gross Amount',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=True,
        help='Quantity × Unit Amount before tax.',
    )
    tax_amount = fields.Monetary(
        string='Tax Amount',
        currency_field='currency_id',
        default=0.0,
        help='Tax amount calculated via Odoo taxes or imported.',
    )
    net_amount = fields.Monetary(
        string='Net Amount',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=True,
        help='Gross Amount + Tax Amount.',
    )
    source_system = fields.Char(
        string='Source System',
        help='External system that imported this charge (e.g. Airbnb, VRBO).',
    )
    source_reference = fields.Char(
        string='Source Reference',
        help='External reference ID from the source system.',
    )
    transaction_date = fields.Date(
        string='Transaction Date',
        required=True,
        index=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    # Link to the original charge for refunds/reversals
    reversal_of_id = fields.Many2one(
        'pms.reservation.charge',
        string='Reversal Of',
        help='If this charge is a refund/reversal, link it to the original charge.',
    )
    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes',
        help='Odoo taxes applied to this charge for accounting.',
    )

    @api.depends('quantity', 'unit_amount', 'tax_amount')
    def _compute_amounts(self):
        for rec in self:
            rec.gross_amount = rec.quantity * rec.unit_amount
            rec.net_amount = rec.gross_amount + rec.tax_amount

    @api.constrains('quantity')
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than zero.'))