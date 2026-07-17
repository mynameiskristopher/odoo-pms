# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmsOwner(models.Model):
    _name = 'pms.owner'
    _description = 'Property Owner'
    _order = 'name'
    _inherit = ['mail.thread']

    # ── Contact Link ───────────────────────────────────────────────────
    partner_id = fields.Many2one(
        'res.partner',
        string='Contact',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='The Odoo contact record for this owner. '
             'All contact details (name, email, phone, address) '
             'are managed on the partner.',
    )

    # ── Related display fields (delegated to partner) ──────────────────
    name = fields.Char(
        related='partner_id.name',
        store=True,
        tracking=True,
    )
    email = fields.Char(
        related='partner_id.email',
    )
    phone = fields.Char(
        related='partner_id.phone',
    )
    website = fields.Char(
        related='partner_id.website',
    )
    # Address fields from partner (read-only display on owner form)
    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one(related='partner_id.state_id')
    zip = fields.Char(related='partner_id.zip')
    country_id = fields.Many2one(related='partner_id.country_id')

    # ── Identity ────────────────────────────────────────────────────────
    owner_type = fields.Selection(
        [('individual', 'Individual'), ('company', 'Company')],
        string='Owner Type',
        required=True,
        default='company',
        tracking=True,
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this owner instead of deleting.',
    )

    # ── Tax / 1099 Information ──────────────────────────────────────────
    tax_type = fields.Selection(
        [
            ('rents', 'Rents'),
            ('other', 'Other'),
            ('none', 'None'),
            ('non_employee_compensation', 'Non-Employee Compensation'),
        ],
        string='1099 Income Classification',
        tracking=True,
        help='1099 Income classification.',
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

    # ── ACH / Payment Information ───────────────────────────────────────
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

    # ── Notes ───────────────────────────────────────────────────────────
    notes = fields.Html(
        string='Notes',
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
    lead_ids = fields.One2many(
        'pms.owner.lead',
        'owner_id',
        string='Owner Leads',
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

    # ── ORM Methods ────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        """Auto-create a res.partner for each owner if not provided."""
        Partner = self.env['res.partner']
        # Find or create the "Owner" partner category
        category = self.env.ref('pms.partner_category_owner', raise_if_not_found=False)
        for vals in vals_list:
            if not vals.get('partner_id'):
                # Pop related fields that should go on the partner instead
                partner_vals = {}
                for fld in ('name', 'email', 'phone', 'website',
                            'street', 'street2', 'city', 'zip'):
                    if vals.get(fld):
                        partner_vals[fld] = vals.pop(fld)
                # Ensure a name
                partner_vals.setdefault('name', 'New Owner')
                # Set company type based on owner_type
                owner_type = vals.get('owner_type', 'company')
                partner_vals['is_company'] = owner_type == 'company'
                partner = Partner.create(partner_vals)
                # Tag with Owner category
                if category:
                    partner.category_id = [(4, category.id)]
                vals['partner_id'] = partner.id
        return super().create(vals_list)

    def write(self, vals):
        """Sync owner_type to partner is_company when changed."""
        if 'owner_type' in vals:
            for rec in self:
                if rec.partner_id:
                    rec.partner_id.is_company = vals['owner_type'] == 'company'
        return super().write(vals)

    def action_open_partner(self):
        """Smart button to open the linked contact."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

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