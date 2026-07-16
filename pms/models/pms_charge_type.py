# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmsChargeType(models.Model):
    _name = 'pms.charge.type'
    _description = 'Property Charge Type'
    _order = 'sequence, id'

    name = fields.Char(
        string='Charge Type Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
        index=True,
        help='Short code used to map imported reservation fee codes.',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    is_revenue = fields.Boolean(
        string='Is Revenue',
        default=True,
        help='If checked, this charge type represents revenue (rent, fees). '
             'If unchecked, it represents a tax, liability, or expense.',
    )
    is_tax = fields.Boolean(
        string='Is Tax',
        default=False,
        help='If checked, this charge is a tax liability and is never counted '
             'as owner or management-company revenue.',
    )
    is_refund = fields.Boolean(
        string='Is Refund / Reversal',
        default=False,
        help='If checked, charges of this type reverse the allocation of an '
             'original charge.',
    )
    is_expense = fields.Boolean(
        string='Is Expense',
        default=False,
        help='If checked, this charge type represents an expense (e.g. '
             'maintenance, OTA commission).',
    )
    product_ids = fields.Many2many(
        'product.product',
        'pms_charge_type_product_rel',
        'charge_type_id',
        'product_id',
        string='Mapped Products',
        help='Odoo products that map to this charge type.',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    note = fields.Text(
        string='Notes',
    )

    @api.model
    def _get_default_charge_types(self):
        """Return a list of dicts for seeding default charge types."""
        return [
            {'name': 'Rent', 'code': 'RENT', 'is_revenue': True},
            {'name': 'Cleaning Fee', 'code': 'CLEANING', 'is_revenue': True},
            {'name': 'Pet Fee', 'code': 'PET_FEE', 'is_revenue': True},
            {'name': 'Damage Waiver', 'code': 'DAMAGE_WAIVER', 'is_revenue': True},
            {'name': 'Resort Fee', 'code': 'RESORT_FEE', 'is_revenue': True},
            {'name': 'Booking Fee', 'code': 'BOOKING_FEE', 'is_revenue': True},
            {'name': 'Cancellation Fee', 'code': 'CANCELLATION_FEE', 'is_revenue': True},
            {'name': 'Early Check-in', 'code': 'EARLY_CHECKIN', 'is_revenue': True},
            {'name': 'Late Checkout', 'code': 'LATE_CHECKOUT', 'is_revenue': True},
            {'name': 'Lodging Tax', 'code': 'LODGING_TAX', 'is_revenue': False, 'is_tax': True},
            {'name': 'Sales Tax', 'code': 'SALES_TAX', 'is_revenue': False, 'is_tax': True},
            {'name': 'OTA Commission', 'code': 'OTA_COMMISSION', 'is_revenue': False, 'is_expense': True},
            {'name': 'Credit Card Fee', 'code': 'CC_FEE', 'is_revenue': False, 'is_expense': True},
            {'name': 'Owner Maintenance Expense', 'code': 'OWNER_MAINT', 'is_revenue': False, 'is_expense': True},
            {'name': 'Discount', 'code': 'DISCOUNT', 'is_revenue': True},
            {'name': 'Refund', 'code': 'REFUND', 'is_revenue': True, 'is_refund': True},
            {'name': 'Security Deposit', 'code': 'SECURITY_DEPOSIT', 'is_revenue': False},
        ]

    @api.constrains('code', 'company_id')
    def _check_code_unique(self):
        for rec in self:
            if self.search_count([
                ('code', '=', rec.code),
                ('company_id', '=', rec.company_id.id),
                ('id', '!=', rec.id),
            ]):
                raise ValidationError(_('Charge type code must be unique per company.'))