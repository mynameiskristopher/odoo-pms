# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmsOwnerAgreement(models.Model):
    _name = 'pms.owner.agreement'
    _description = 'Property Owner Agreement'
    _order = 'effective_start_date desc, id desc'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Agreement Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('pms.owner.agreement') or 'New',
    )
    owner_id = fields.Many2one(
        'pms.owner',
        string='Owner',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
    )
    property_id = fields.Many2one(
        'pms.property',
        string='Property',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
    )
    effective_start_date = fields.Date(
        string='Effective From',
        required=True,
        index=True,
        tracking=True,
    )
    effective_end_date = fields.Date(
        string='Effective To',
        index=True,
        tracking=True,
        help='Leave blank for an open-ended agreement.',
    )
    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('terminated', 'Terminated'),
        ],
        string='Status',
        required=True,
        default='draft',
        tracking=True,
    )
    settlement_frequency = fields.Selection(
        [
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        string='Settlement Frequency',
        required=True,
        default='monthly',
        tracking=True,
    )
    revenue_policy_id = fields.Many2one(
        'pms.revenue.policy',
        string='Revenue Policy',
        required=True,
        ondelete='restrict',
        tracking=True,
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
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        help='Analytic account used for settlement accounting entries '
             'so revenue and expenses can be reported by property.',
    )
    note = fields.Text(
        string='Notes',
    )

    @api.constrains('name', 'company_id')
    def _check_name_unique(self):
        for rec in self:
            if self.search_count([
                ('name', '=', rec.name),
                ('company_id', '=', rec.company_id.id),
                ('id', '!=', rec.id),
            ]):
                raise ValidationError(_('Agreement reference must be unique per company.'))

    @api.constrains('effective_start_date', 'effective_end_date')
    def _check_dates(self):
        for rec in self:
            if rec.effective_end_date and rec.effective_end_date < rec.effective_start_date:
                raise ValidationError(_('Effective end date must be on or after the start date.'))

    @api.constrains('property_id', 'effective_start_date', 'effective_end_date', 'status')
    def _check_no_overlapping_active(self):
        """Prevent overlapping active agreements for the same property."""
        for rec in self:
            if rec.status != 'active':
                continue
            domain = [
                ('property_id', '=', rec.property_id.id),
                ('status', '=', 'active'),
                ('id', '!=', rec.id),
            ]
            others = self.search(domain)
            for other in others:
                # Date-range overlap check
                start_a = rec.effective_start_date
                end_a = rec.effective_end_date or fields.Date.to_date('2099-12-31')
                start_b = other.effective_start_date
                end_b = other.effective_end_date or fields.Date.to_date('2099-12-31')
                if start_a <= end_b and start_b <= end_a:
                    raise ValidationError(_(
                        'Overlapping active agreements are not allowed for property "%s". '
                        'Existing agreement %s overlaps with this one.'
                    ) % (rec.property_id.name, other.name))

    # ── Actions ─────────────────────────────────────────────────────────

    def action_activate(self):
        for rec in self:
            rec.status = 'active'

    def action_terminate(self):
        for rec in self:
            rec.status = 'terminated'

    def action_expire(self):
        for rec in self:
            rec.status = 'expired'

    # ── Lookup helpers ──────────────────────────────────────────────────

    @api.model
    def find_active_agreement(self, property_id, date):
        """
        Return the active owner agreement for *property_id* on *date*,
        or an empty recordset if none exists.
        """
        if not property_id or not date:
            return self.env['pms.owner.agreement']
        domain = [
            ('property_id', '=', property_id),
            ('status', '=', 'active'),
            ('effective_start_date', '<=', date),
            '|',
            ('effective_end_date', '=', False),
            ('effective_end_date', '>=', date),
        ]
        return self.search(domain, limit=1)

    # ── Calculation Preview ─────────────────────────────────────────────

    @api.model
    def preview_calculation(self, agreement_id, sample_lines):
        """
        Given an agreement ID and a list of sample charge dicts:
            [{'charge_type_code': 'RENT', 'gross_amount': 1000.0, 'tax_amount': 0.0}, ...]

        Return a dict with the calculated breakdown:
            owner_gross_proceeds, commission_base, management_fee,
            manager_revenue, taxes_liabilities, owner_expenses, owner_net_payout,
            line_details
        """
        agreement = self.browse(agreement_id)
        if not agreement:
            raise ValidationError(_('Agreement not found.'))
        policy = agreement.revenue_policy_id
        ChargeType = self.env['pms.charge.type']

        owner_gross = 0.0
        commission_base = 0.0
        manager_revenue = 0.0
        taxes_liabilities = 0.0
        owner_expenses = 0.0
        line_details = []

        for sample in sample_lines:
            code = sample.get('charge_type_code')
            gross = float(sample.get('gross_amount', 0.0))
            tax = float(sample.get('tax_amount', 0.0))
            charge_type = ChargeType.search([('code', '=', code)], limit=1)
            if not charge_type:
                raise ValidationError(_('No charge type found for code "%s".') % code)

            line = policy.line_ids.filtered(
                lambda l: l.charge_type_id == charge_type and l.active
            )[:1]
            if not line:
                # No matching policy line — unknown charge
                line_details.append({
                    'charge_type': charge_type.name,
                    'gross_amount': gross,
                    'owner_amount': 0.0,
                    'manager_amount': 0.0,
                    'liability_amount': 0.0,
                    'commissionable_amount': 0.0,
                    'management_fee_amount': 0.0,
                    'warning': 'No policy line for this charge type.',
                })
                continue

            owner_amt = policy._round_amount(gross * (line.owner_share_percent / 100.0))
            manager_amt = policy._round_amount(gross * (line.manager_share_percent / 100.0))
            liability_amt = policy._round_amount(gross * (line.liability_share_percent / 100.0))

            # Commissionable amount
            if line.commission_basis == 'excluded':
                commissionable = 0.0
            elif line.commission_basis == 'gross_amount':
                commissionable = gross
            elif line.commission_basis == 'owner_allocated_amount':
                commissionable = owner_amt
            else:
                commissionable = 0.0

            commission_base += commissionable
            taxes_liabilities += tax + liability_amt

            if charge_type.is_revenue and not charge_type.is_refund:
                owner_gross += owner_amt
                manager_revenue += manager_amt
            elif charge_type.is_expense:
                # Expense allocation
                if line.expense_responsibility == 'owner':
                    owner_expenses += gross
                elif line.expense_responsibility == 'manager':
                    manager_revenue -= gross
                elif line.expense_responsibility == 'split':
                    owner_expenses += gross / 2.0
                    manager_revenue -= gross / 2.0
            elif charge_type.is_tax:
                taxes_liabilities += gross

            line_details.append({
                'charge_type': charge_type.name,
                'gross_amount': gross,
                'owner_amount': owner_amt,
                'manager_amount': manager_amt,
                'liability_amount': liability_amt,
                'commissionable_amount': commissionable,
                'expense_responsibility': line.expense_responsibility,
            })

        management_fee = policy.calculate_management_fee(commission_base)
        owner_net = owner_gross - management_fee - owner_expenses

        return {
            'owner_gross_proceeds': owner_gross,
            'commission_base': commission_base,
            'management_fee': management_fee,
            'manager_revenue': manager_revenue,
            'taxes_liabilities': taxes_liabilities,
            'owner_expenses': owner_expenses,
            'owner_net_payout': owner_net,
            'line_details': line_details,
        }