# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmsOwner(models.Model):
    _name = 'pms.owner'
    _description = 'Property Owner'
    _order = 'name'
    _rec_name = 'name'
    _inherit = ['mail.thread']

    # ── Identity ────────────────────────────────────────────────────────
    owner_type = fields.Selection(
        [('owner', 'Owner')],
        string='Type',
        required=True,
        default='owner',
        tracking=True,
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this owner instead of deleting.',
    )

    name = fields.Char(
        string='Company Name',
        required=True,
        tracking=True,
        help='Name of the owning company or individual.',
    )

    # ── Primary Address ─────────────────────────────────────────────────
    street_address = fields.Char(
        string='Street Address',
        help='Street address of the company.',
    )
    extended_address = fields.Char(
        string='Extended Address',
        help='Extended address (apt, suite, etc.).',
    )
    locality = fields.Char(
        string='City / Locality',
        help='City or locality.',
    )
    region = fields.Char(
        string='State / Region',
        help='State or region.',
    )
    postal = fields.Char(
        string='Postal Code',
        help='Postal / ZIP code of the company.',
    )
    country = fields.Char(
        string='Country',
        size=2,
        help='ISO 3166-1 alpha-2 country code (2 characters).',
    )

    # ── Tax / 1099 Information (Restricted) ──────────────────────────────
    tax_type = fields.Selection(
        [
            ('rents', 'Rents'),
            ('other', 'Other'),
            ('none', 'None'),
            ('non_employee_compensation', 'Non-Employee Compensation'),
        ],
        string='1099 Income Classification',
        tracking=True,
        help='1099 Income classification (Restricted).',
    )
    tax_name = fields.Char(
        string='1099 Tax Payee Name',
        required=True,
        tracking=True,
        help='1099 Tax Payee Name, if different from the owner name.',
    )
    tax_id = fields.Char(
        string='1099 Tax ID',
        help='1099 Tax ID.',
    )

    # ── ACH / Payment Information (Restricted) ──────────────────────────
    ach_account_number = fields.Char(
        string='ACH Account Number',
        help='ACH Account Number.',
    )
    ach_routing_number = fields.Char(
        string='ACH Routing Number',
        size=9,
        help='ACH Routing Number – exactly 9 digits.',
    )
    ach_account_type = fields.Selection(
        [
            ('business-checking', 'Business Checking'),
            ('business-savings', 'Business Savings'),
            ('personal-checking', 'Personal Checking'),
            ('personal-savings', 'Personal Savings'),
        ],
        string='ACH Account Type',
        help='Used if payment type is ACH.',
    )
    ach_verified_at = fields.Datetime(
        string='ACH Verified At',
        help='When ACH information was pre-noted.',
    )
    payment_type = fields.Selection(
        [
            ('print', 'Print / Check'),
            ('direct', 'Direct / ACH'),
        ],
        string='Payment Type',
        help='Payment type, used for ACH or Check payments.',
    )

    # ── Insurance (Deprecated) ──────────────────────────────────────────
    gl_expiration_date = fields.Date(
        string='GL Expiration Date',
        help='General liability insurance expiration date (Deprecated).',
    )
    gl_insurance_policy = fields.Char(
        string='GL Insurance Policy',
        help='General liability insurance policy number (Deprecated).',
    )
    wc_expiration_date = fields.Date(
        string='WC Expiration Date',
        help='Workers comp insurance expiration date (Deprecated).',
    )
    wc_insurance_policy = fields.Char(
        string='WC Insurance Policy',
        help='Workers comp insurance policy number (Deprecated).',
    )

    # ── Travel Agent / Commission ───────────────────────────────────────
    travel_agent_deduct_commission = fields.Boolean(
        string='Deduct Travel Agent Commission',
        default=False,
        help='Enable travel agent commission deduction.',
    )
    travel_agent_commission = fields.Float(
        string='Travel Agent Commission %',
        digits=(5, 2),
        help='Commission value between 0 and 100%.',
    )
    travel_agent_iata_number = fields.Char(
        string='IATA Number',
        help='IATA number – required for all travel agents.',
    )

    # ── Work Order ──────────────────────────────────────────────────────
    enable_work_order_approval = fields.Boolean(
        string='Enable Work Order Approval',
        default=False,
        help='Allow vendor/owner to approve assigned work orders.',
    )

    # ── Contact Details ─────────────────────────────────────────────────
    notes = fields.Html(
        string='Notes',
    )
    website = fields.Char(
        string='Website',
    )
    email = fields.Char(
        string='Email',
    )
    fax = fields.Char(
        string='Fax',
        help='Use E.164 format. Non-compliant numbers processed within US locale.',
    )
    phone = fields.Char(
        string='Phone',
        help='Use E.164 format. Non-compliant numbers processed within US locale.',
    )

    # ── Tags ────────────────────────────────────────────────────────────
    tag_ids = fields.Many2many(
        'pms.owner.tag',
        'pms_owner_tag_rel',
        'owner_id',
        'tag_id',
        string='Tags',
    )

    # ── Tax Address ────────────────────────────────────────────────────
    tax_street_address = fields.Char(
        string='Tax Street Address',
        required=True,
    )
    tax_extended_address = fields.Char(
        string='Tax Extended Address',
        required=True,
    )
    tax_locality = fields.Char(
        string='Tax City / Locality',
        required=True,
    )
    tax_region = fields.Char(
        string='Tax State / Region',
        required=True,
    )
    tax_postal_code = fields.Char(
        string='Tax Postal Code',
        required=True,
    )
    tax_country = fields.Char(
        string='Tax Country',
        size=2,
        required=True,
        help='ISO 3166-1 alpha-2 country code (2 characters).',
    )
    tax_phone = fields.Char(
        string='Tax Phone',
        required=True,
    )

    # ── Financial / Administrative ──────────────────────────────────────
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    always_show_in_statements = fields.Boolean(
        string='Always Show in Statements',
        default=False,
    )
    split_with_contacts = fields.Boolean(
        string='Split with Contacts',
        default=False,
    )
    agent_commission = fields.Char(
        string='Agent Commission',
    )
    current_balance = fields.Monetary(
        string='Current Balance',
        currency_field='currency_id',
    )
    minimum_balance = fields.Monetary(
        string='Minimum Balance',
        currency_field='currency_id',
    )
    opening_balance = fields.Monetary(
        string='Opening Balance',
        required=True,
        currency_field='currency_id',
        default=0.0,
    )

    # ── Relationships ──────────────────────────────────────────────────
    unit_owner_ids = fields.One2many(
        'pms.unit.owner',
        'owner_id',
        string='Unit Ownership',
    )

    # ── Currency (for monetary widget) ─────────────────────────────────
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute='_compute_currency_id',
    )

    @api.depends('company_id')
    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = rec.company_id.currency_id or self.env.company.currency_id

    # ── Constraints ────────────────────────────────────────────────────
    @api.constrains('travel_agent_commission')
    def _check_travel_agent_commission(self):
        for rec in self:
            if rec.travel_agent_commission and (rec.travel_agent_commission < 0 or rec.travel_agent_commission > 100):
                raise ValidationError(_('Travel Agent Commission must be between 0 and 100.'))

    @api.constrains('ach_routing_number')
    def _check_ach_routing_number(self):
        for rec in self:
            if rec.ach_routing_number and len(rec.ach_routing_number) != 9:
                raise ValidationError(_('ACH Routing Number must be exactly 9 digits.'))

    @api.constrains('country')
    def _check_country(self):
        for rec in self:
            if rec.country and len(rec.country) != 2:
                raise ValidationError(_('Country must be a 2-character ISO code.'))

    @api.constrains('tax_country')
    def _check_tax_country(self):
        for rec in self:
            if rec.tax_country and len(rec.tax_country) != 2:
                raise ValidationError(_('Tax Country must be a 2-character ISO code.'))


class PmsOwnerTag(models.Model):
    _name = 'pms.owner.tag'
    _description = 'Owner Tag'
    _order = 'name'

    name = fields.Char(
        string='Tag Name',
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    color = fields.Integer(
        string='Color Index',
    )