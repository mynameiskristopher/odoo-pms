# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmsOwnerSettlement(models.Model):
    _name = 'pms.owner.settlement'
    _description = 'Property Owner Settlement'
    _order = 'period_start desc, id desc'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Settlement Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('pms.owner.settlement') or 'New',
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
    agreement_id = fields.Many2one(
        'pms.owner.agreement',
        string='Owner Agreement',
        ondelete='restrict',
        index=True,
    )
    policy_id = fields.Many2one(
        'pms.revenue.policy',
        string='Revenue Policy',
        ondelete='restrict',
        index=True,
    )
    period_start = fields.Date(
        string='Period Start',
        required=True,
        index=True,
        tracking=True,
    )
    period_end = fields.Date(
        string='Period End',
        required=True,
        index=True,
        tracking=True,
    )

    # ── Calculated Amounts ──────────────────────────────────────────────
    owner_gross_proceeds = fields.Monetary(
        string='Owner Gross Proceeds',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
    )
    commission_base = fields.Monetary(
        string='Commission Base',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
    )
    management_fee = fields.Monetary(
        string='Management Fee',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
    )
    owner_expenses = fields.Monetary(
        string='Owner Expenses',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
    )
    owner_credits = fields.Monetary(
        string='Owner Credits',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
    )
    owner_net_payout = fields.Monetary(
        string='Owner Net Payout',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
    )
    tax_liability = fields.Monetary(
        string='Tax & Liability',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('calculated', 'Calculated'),
            ('reviewed', 'Reviewed'),
            ('finalized', 'Finalized'),
            ('paid', 'Paid'),
            ('cancelled', 'Cancelled'),
            ('exception', 'Exception'),
        ],
        string='State',
        required=True,
        default='draft',
        tracking=True,
        copy=False,
    )
    finalized_at = fields.Datetime(
        string='Finalized At',
        readonly=True,
        copy=False,
    )

    # ── Historical Snapshot (immutable after finalize) ──────────────────
    snapshot_agreement_data = fields.Text(
        string='Agreement Snapshot',
        readonly=True,
        copy=False,
        help='JSON snapshot of the agreement at finalization time.',
    )
    snapshot_policy_data = fields.Text(
        string='Policy Snapshot',
        readonly=True,
        copy=False,
        help='JSON snapshot of the revenue policy at finalization time.',
    )
    snapshot_management_fee_rate = fields.Float(
        string='Management Fee Rate (Snapshot)',
        digits=(5, 2),
        readonly=True,
        copy=False,
    )
    snapshot_management_fee_type = fields.Char(
        string='Management Fee Type (Snapshot)',
        readonly=True,
        copy=False,
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
        help='Analytic account for reporting revenue and expenses by property.',
    )
    line_ids = fields.One2many(
        'pms.owner.settlement.line',
        'settlement_id',
        string='Settlement Lines',
        copy=True,
    )
    note = fields.Text(
        string='Notes',
    )
    exception_note = fields.Text(
        string='Exception Details',
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)',
         'Settlement reference must be unique per company.'),
    ]

    @api.constrains('period_start', 'period_end')
    def _check_period(self):
        for rec in self:
            if rec.period_end < rec.period_start:
                raise ValidationError(_('Period end must be on or after period start.'))

    @api.depends('line_ids', 'line_ids.owner_amount', 'line_ids.manager_amount',
                 'line_ids.liability_amount', 'line_ids.commissionable_amount',
                 'line_ids.management_fee_amount')
    def _compute_totals(self):
        for rec in self:
            owner_gross = 0.0
            commission_base = 0.0
            management_fee = 0.0
            owner_exp = 0.0
            owner_cred = 0.0
            tax_liab = 0.0

            for line in rec.line_ids:
                ct = line.charge_type_id
                if ct and ct.is_revenue and not ct.is_refund:
                    owner_gross += line.owner_amount
                elif ct and ct.is_refund:
                    owner_gross -= line.owner_amount
                elif ct and ct.is_tax:
                    tax_liab += line.liability_amount
                elif ct and ct.is_expense:
                    if line.expense_responsibility == 'owner':
                        owner_exp += line.gross_amount
                    elif line.expense_responsibility == 'split':
                        owner_exp += line.gross_amount / 2.0

                commission_base += line.commissionable_amount
                management_fee += line.management_fee_amount
                tax_liab += line.liability_amount

                # Owner credits (negative charges)
                if line.gross_amount < 0 and ct and ct.is_revenue and not ct.is_refund:
                    owner_cred += abs(line.owner_amount)

            rec.owner_gross_proceeds = owner_gross
            rec.commission_base = commission_base
            rec.management_fee = management_fee
            rec.owner_expenses = owner_exp
            rec.owner_credits = owner_cred
            rec.tax_liability = tax_liab
            rec.owner_net_payout = owner_gross - management_fee - owner_exp + owner_cred

    # ── State Transitions ───────────────────────────────────────────────

    def action_calculate(self):
        """Calculate settlement lines from reservation charges in the period."""
        for rec in self:
            if rec.state not in ('draft', 'exception'):
                raise ValidationError(_('Settlement must be in draft or exception state to calculate.'))
            rec._calculate_lines()
            rec.state = 'calculated'

    def action_review(self):
        for rec in self:
            if rec.state != 'calculated':
                raise ValidationError(_('Settlement must be calculated before review.'))
            rec.state = 'reviewed'

    def action_finalize(self):
        """Finalize the settlement and store immutable snapshots."""
        for rec in self:
            if rec.state != 'reviewed':
                raise ValidationError(_('Settlement must be reviewed before finalizing.'))
            rec._store_snapshot()
            rec.finalized_at = fields.Datetime.now()
            rec.state = 'finalized'

    def action_pay(self):
        for rec in self:
            if rec.state != 'finalized':
                raise ValidationError(_('Settlement must be finalized before marking as paid.'))
            rec.state = 'paid'

    def action_cancel(self):
        for rec in self:
            if rec.state == 'finalized':
                raise ValidationError(_('Finalized settlements cannot be cancelled.'))
            rec.state = 'cancelled'

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state in ('exception', 'calculated'):
                rec.state = 'draft'

    # ── Calculation Engine ──────────────────────────────────────────────

    def _calculate_lines(self):
        """
        For every reservation charge in the settlement period:
        1. Find the active owner agreement for the property on the charge date.
        2. Find the matching revenue policy line for the charge type.
        3. Calculate owner/manager/liability amounts.
        4. Determine commissionable amount.
        5. Sum commissionable amounts to get commission base.
        6. Calculate management fee using the policy.
        """
        self.ensure_one()
        SettlementLine = self.env['pms.owner.settlement.line']
        ChargeType = self.env['pms.charge.type']

        # Clear existing lines
        self.line_ids.unlink()

        # Find all reservation charges in the period for this property
        charges = self.env['pms.reservation.charge'].search([
            ('reservation_id.property_id', '=', self.property_id.id),
            ('transaction_date', '>=', self.period_start),
            ('transaction_date', '<=', self.period_end),
        ])

        if not charges:
            return

        # Find the agreement
        agreement = self.agreement_id or self.env['pms.owner.agreement'].find_active_agreement(
            self.property_id.id, self.period_start
        )
        if not agreement:
            self.state = 'exception'
            self.exception_note = _('No active owner agreement found for property %s in the period.') % self.property_id.name
            return

        policy = agreement.revenue_policy_id
        self.agreement_id = agreement
        self.policy_id = policy

        exception_notes = []
        commission_base = 0.0
        line_vals_list = []

        for charge in charges:
            charge_type = charge.charge_type_id
            policy_line = policy.line_ids.filtered(
                lambda l: l.charge_type_id == charge_type and l.active
            )[:1]

            if not policy_line:
                exception_notes.append(_(
                    'Charge type "%s" on reservation %s has no mapping in revenue policy "%s".'
                ) % (charge_type.name, charge.reservation_id.name, policy.name))
                # Still create a line with zeros and a warning so it's visible
                line_vals = {
                    'settlement_id': self.id,
                    'reservation_id': charge.reservation_id.id,
                    'reservation_charge_id': charge.id,
                    'charge_type_id': charge_type.id,
                    'gross_amount': charge.gross_amount,
                    'owner_amount': 0.0,
                    'manager_amount': 0.0,
                    'liability_amount': 0.0,
                    'commissionable_amount': 0.0,
                    'management_fee_amount': 0.0,
                    'expense_responsibility': 'owner',
                    'calculation_description': 'UNMAPPED CHARGE TYPE — no policy line found.',
                }
                line_vals_list.append(line_vals)
                continue

            gross = charge.gross_amount
            is_refund = charge_type.is_refund or (charge.reversal_of_id and True)

            # Calculate allocations
            owner_pct = policy_line.owner_share_percent / 100.0
            manager_pct = policy_line.manager_share_percent / 100.0
            liability_pct = policy_line.liability_share_percent / 100.0

            if is_refund:
                # Reverse the original allocation
                owner_amt = -(abs(gross) * owner_pct)
                manager_amt = -(abs(gross) * manager_pct)
                liability_amt = -(abs(gross) * liability_pct)
                desc = 'REVERSAL of original allocation.'
            else:
                owner_amt = policy._round_amount(gross * owner_pct)
                manager_amt = policy._round_amount(gross * manager_pct)
                liability_amt = policy._round_amount(gross * liability_pct)
                desc = ''

            # Commissionable amount
            if is_refund:
                # Reverse commission basis
                if policy_line.commission_basis == 'excluded':
                    commissionable = 0.0
                elif policy_line.commission_basis == 'gross_amount':
                    commissionable = -abs(gross)
                elif policy_line.commission_basis == 'owner_allocated_amount':
                    commissionable = owner_amt
                else:
                    commissionable = 0.0
            else:
                if policy_line.commission_basis == 'excluded':
                    commissionable = 0.0
                elif policy_line.commission_basis == 'gross_amount':
                    commissionable = gross
                elif policy_line.commission_basis == 'owner_allocated_amount':
                    commissionable = owner_amt
                else:
                    commissionable = 0.0

            commission_base += commissionable

            # Build calculation description
            if not desc:
                desc = 'Owner: %.2f%% (%.2f), Manager: %.2f%% (%.2f), Liability: %.2f%% (%.2f), Commission basis: %s (%.2f)' % (
                    policy_line.owner_share_percent, owner_amt,
                    policy_line.manager_share_percent, manager_amt,
                    policy_line.liability_share_percent, liability_amt,
                    policy_line.commission_basis, commissionable,
                )

            line_vals = {
                'settlement_id': self.id,
                'reservation_id': charge.reservation_id.id,
                'reservation_charge_id': charge.id,
                'charge_type_id': charge_type.id,
                'gross_amount': gross,
                'owner_amount': owner_amt,
                'manager_amount': manager_amt,
                'liability_amount': liability_amt,
                'commissionable_amount': commissionable,
                'management_fee_amount': 0.0,  # Set after summing
                'expense_responsibility': policy_line.expense_responsibility,
                'calculation_description': desc,
            }
            line_vals_list.append(line_vals)

        # Create all lines
        created_lines = SettlementLine.create(line_vals_list)

        # Calculate management fee on the total commission base
        management_fee = policy.calculate_management_fee(commission_base)

        # Distribute management fee across lines proportionally to their commissionable amount
        if commission_base != 0 and management_fee != 0:
            for line in created_lines:
                if line.commissionable_amount != 0:
                    ratio = line.commissionable_amount / commission_base
                    line.management_fee_amount = policy._round_amount(management_fee * ratio)
        elif management_fee != 0 and created_lines:
            # If commission_base is 0 but there's a minimum fee, assign to first revenue line
            revenue_lines = created_lines.filtered(
                lambda l: l.charge_type_id.is_revenue and not l.charge_type_id.is_refund
            )
            if revenue_lines:
                revenue_lines[0].management_fee_amount = management_fee

        # Handle exceptions
        if exception_notes:
            self.state = 'exception'
            self.exception_note = '\n'.join(exception_notes)

    def _store_snapshot(self):
        """Store immutable JSON snapshots of agreement and policy data."""
        import json
        self.ensure_one()
        agreement = self.agreement_id
        policy = self.policy_id

        agreement_data = {
            'name': agreement.name,
            'owner_id': agreement.owner_id.id,
            'owner_name': agreement.owner_id.name,
            'property_id': agreement.property_id.id,
            'property_name': agreement.property_id.name,
            'effective_start_date': str(agreement.effective_start_date) if agreement.effective_start_date else None,
            'effective_end_date': str(agreement.effective_end_date) if agreement.effective_end_date else None,
            'settlement_frequency': agreement.settlement_frequency,
            'revenue_policy_id': agreement.revenue_policy_id.id,
        }

        policy_data = {
            'name': policy.name,
            'management_fee_type': policy.management_fee_type,
            'management_fee_percent': policy.management_fee_percent,
            'management_fee_fixed_amount': policy.management_fee_fixed_amount,
            'minimum_management_fee': policy.minimum_management_fee,
            'maximum_management_fee': policy.maximum_management_fee,
            'rounding_method': policy.rounding_method,
            'lines': [],
        }
        for line in policy.line_ids.filtered(lambda l: l.active):
            policy_data['lines'].append({
                'charge_type': line.charge_type_id.name,
                'charge_type_code': line.charge_type_id.code,
                'owner_share_percent': line.owner_share_percent,
                'manager_share_percent': line.manager_share_percent,
                'liability_share_percent': line.liability_share_percent,
                'commission_basis': line.commission_basis,
                'expense_responsibility': line.expense_responsibility,
            })

        self.snapshot_agreement_data = json.dumps(agreement_data, default=str)
        self.snapshot_policy_data = json.dumps(policy_data, default=str)
        self.snapshot_management_fee_rate = policy.management_fee_percent
        self.snapshot_management_fee_type = policy.management_fee_type

    # ── Write override: prevent changes after finalization ──────────────

    def write(self, vals):
        for rec in self:
            if rec.state == 'finalized' or rec.state == 'paid':
                # Allow only state changes to paid (for finalized) or note updates
                allowed_keys = {'state', 'finalized_at', 'note'}
                if rec.state == 'paid':
                    allowed_keys = {'note'}
                attempted = set(vals.keys()) - allowed_keys
                if attempted:
                    raise ValidationError(_(
                        'Finalized/paid settlements are immutable. '
                        'Cannot modify fields: %s'
                    ) % ', '.join(sorted(attempted)))
        return super().write(vals)


class PmsOwnerSettlementLine(models.Model):
    _name = 'pms.owner.settlement.line'
    _description = 'Property Owner Settlement Line'
    _order = 'reservation_id, id'

    settlement_id = fields.Many2one(
        'pms.owner.settlement',
        string='Settlement',
        required=True,
        ondelete='cascade',
        index=True,
    )
    reservation_id = fields.Many2one(
        'pms.booking',
        string='Reservation',
        ondelete='restrict',
        index=True,
    )
    reservation_charge_id = fields.Many2one(
        'pms.reservation.charge',
        string='Reservation Charge',
        ondelete='restrict',
    )
    charge_type_id = fields.Many2one(
        'pms.charge.type',
        string='Charge Type',
        required=True,
        ondelete='restrict',
    )
    gross_amount = fields.Monetary(
        string='Gross Amount',
        currency_field='currency_id',
    )
    owner_amount = fields.Monetary(
        string='Owner Amount',
        currency_field='currency_id',
    )
    manager_amount = fields.Monetary(
        string='Manager Amount',
        currency_field='currency_id',
    )
    liability_amount = fields.Monetary(
        string='Liability Amount',
        currency_field='currency_id',
    )
    commissionable_amount = fields.Monetary(
        string='Commissionable Amount',
        currency_field='currency_id',
    )
    management_fee_amount = fields.Monetary(
        string='Management Fee Amount',
        currency_field='currency_id',
    )
    expense_responsibility = fields.Selection(
        [
            ('owner', 'Owner'),
            ('manager', 'Manager'),
            ('split', 'Split 50/50'),
        ],
        string='Expense Responsibility',
        default='owner',
    )
    calculation_description = fields.Text(
        string='Calculation Description',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='settlement_id.currency_id',
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='settlement_id.company_id',
        store=True,
    )