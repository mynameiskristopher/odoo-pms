# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmsRevenuePolicy(models.Model):
    _name = 'pms.revenue.policy'
    _description = 'Property Revenue Policy'
    _order = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Policy Name',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    management_fee_type = fields.Selection(
        [
            ('percentage', 'Percentage'),
            ('fixed', 'Fixed Amount'),
            ('percentage_plus_fixed', 'Percentage + Fixed'),
            ('tiered', 'Tiered'),
        ],
        string='Management Fee Type',
        required=True,
        default='percentage',
        tracking=True,
    )
    management_fee_percent = fields.Float(
        string='Management Fee %',
        digits=(5, 2),
        default=0.0,
        tracking=True,
        help='Percentage used when fee type is "percentage" or "percentage_plus_fixed".',
    )
    management_fee_fixed_amount = fields.Monetary(
        string='Management Fee Fixed Amount',
        currency_field='currency_id',
        default=0.0,
        tracking=True,
        help='Fixed amount used when fee type is "fixed" or "percentage_plus_fixed".',
    )
    minimum_management_fee = fields.Monetary(
        string='Minimum Management Fee',
        currency_field='currency_id',
        default=0.0,
        help='The management fee will not fall below this amount.',
    )
    maximum_management_fee = fields.Monetary(
        string='Maximum Management Fee',
        currency_field='currency_id',
        default=0.0,
        help='The management fee will not exceed this amount (0 = no cap).',
    )
    effective_start_date = fields.Date(
        string='Effective From',
        tracking=True,
    )
    effective_end_date = fields.Date(
        string='Effective To',
        tracking=True,
    )
    rounding_method = fields.Selection(
        [
            ('round', 'Round to Cent'),
            ('round_up', 'Round Up'),
            ('round_down', 'Round Down'),
            ('no_rounding', 'No Rounding'),
        ],
        string='Rounding Method',
        required=True,
        default='round',
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
    line_ids = fields.One2many(
        'pms.revenue.policy.line',
        'policy_id',
        string='Revenue Allocation Lines',
        copy=True,
    )
    note = fields.Text(
        string='Notes',
    )

    @api.constrains('effective_start_date', 'effective_end_date')
    def _check_dates(self):
        for rec in self:
            if rec.effective_start_date and rec.effective_end_date:
                if rec.effective_end_date < rec.effective_start_date:
                    raise ValidationError(_('Effective end date must be on or after the start date.'))

    @api.constrains('management_fee_percent')
    def _check_fee_percent(self):
        for rec in self:
            if rec.management_fee_percent < 0 or rec.management_fee_percent > 100:
                raise ValidationError(_('Management Fee % must be between 0 and 100.'))

    # ── Calculation helpers ────────────────────────────────────────────

    def _round_amount(self, amount):
        """Apply the policy's rounding method to *amount*."""
        self.ensure_one()
        if self.rounding_method == 'no_rounding':
            return amount
        if self.rounding_method == 'round_up':
            import math
            return math.ceil(amount * 100) / 100.0
        if self.rounding_method == 'round_down':
            import math
            return math.floor(amount * 100) / 100.0
        # default: round
        return round(amount, 2)

    def calculate_management_fee(self, commission_base):
        """
        Given the *commission_base* (sum of commissionable amounts),
        return the management fee, clamped to [minimum, maximum].
        """
        self.ensure_one()
        fee = 0.0
        if self.management_fee_type == 'percentage':
            fee = commission_base * (self.management_fee_percent / 100.0)
        elif self.management_fee_type == 'fixed':
            fee = self.management_fee_fixed_amount
        elif self.management_fee_type == 'percentage_plus_fixed':
            fee = (commission_base * (self.management_fee_percent / 100.0)) + self.management_fee_fixed_amount
        elif self.management_fee_type == 'tiered':
            # Placeholder — tiered logic to be implemented later
            fee = commission_base * (self.management_fee_percent / 100.0)

        fee = self._round_amount(fee)

        # Apply minimum / maximum caps
        if self.minimum_management_fee and fee < self.minimum_management_fee:
            fee = self.minimum_management_fee
        if self.maximum_management_fee and fee > self.maximum_management_fee:
            fee = self.maximum_management_fee
        return fee


class PmsRevenuePolicyLine(models.Model):
    _name = 'pms.revenue.policy.line'
    _description = 'Property Revenue Policy Line'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    policy_id = fields.Many2one(
        'pms.revenue.policy',
        string='Revenue Policy',
        required=True,
        ondelete='cascade',
        index=True,
    )
    charge_type_id = fields.Many2one(
        'pms.charge.type',
        string='Charge Type',
        required=True,
        ondelete='restrict',
    )
    owner_share_percent = fields.Float(
        string='Owner Share %',
        digits=(5, 2),
        default=100.0,
        help='Percentage of this charge allocated to the owner.',
    )
    manager_share_percent = fields.Float(
        string='Manager Share %',
        digits=(5, 2),
        default=0.0,
        help='Percentage of this charge allocated to the management company.',
    )
    liability_share_percent = fields.Float(
        string='Liability Share %',
        digits=(5, 2),
        default=0.0,
        help='Percentage of this charge allocated to tax / liability.',
    )
    commission_basis = fields.Selection(
        [
            ('excluded', 'Excluded'),
            ('gross_amount', 'Gross Amount'),
            ('owner_allocated_amount', 'Owner Allocated Amount'),
        ],
        string='Commission Basis',
        required=True,
        default='excluded',
        help='Determines how this charge contributes to the management fee '
             'commission base.',
    )
    expense_responsibility = fields.Selection(
        [
            ('owner', 'Owner'),
            ('manager', 'Manager'),
            ('split', 'Split 50/50'),
        ],
        string='Expense Responsibility',
        default='owner',
        help='For expense charge types, determines who bears the cost.',
    )
    effective_start_date = fields.Date(
        string='Effective From',
    )
    effective_end_date = fields.Date(
        string='Effective To',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    note = fields.Char(
        string='Notes',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='policy_id.company_id',
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='policy_id.currency_id',
        store=True,
    )

    @api.constrains('owner_share_percent', 'manager_share_percent', 'liability_share_percent')
    def _check_allocation_percent(self):
        """Owner + Manager + Liability must total 100 for revenue lines."""
        for rec in self:
            total = rec.owner_share_percent + rec.manager_share_percent + rec.liability_share_percent
            if rec.charge_type_id.is_revenue and not rec.charge_type_id.is_refund:
                if abs(total - 100.0) > 0.01:
                    raise ValidationError(_(
                        'Allocation percentages for revenue charge type "%s" must total 100%% '
                        '(currently %.2f%%).'
                    ) % (rec.charge_type_id.name, total))
            # For non-revenue (tax/expense) lines, shares can be 0
            for label, val in [
                ('Owner Share', rec.owner_share_percent),
                ('Manager Share', rec.manager_share_percent),
                ('Liability Share', rec.liability_share_percent),
            ]:
                if val < 0 or val > 100:
                    raise ValidationError(_('%s must be between 0 and 100.') % label)

    @api.constrains('effective_start_date', 'effective_end_date')
    def _check_dates(self):
        for rec in self:
            if rec.effective_start_date and rec.effective_end_date:
                if rec.effective_end_date < rec.effective_start_date:
                    raise ValidationError(_('Line effective end date must be on or after the start date.'))