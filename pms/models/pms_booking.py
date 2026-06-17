# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PmsBooking(models.Model):
    _name = 'pms.booking'
    _description = 'Vacation Rental Booking'
    _order = 'checkin_date desc, id desc'

    name = fields.Char(
        string='Booking Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('pms.booking') or 'New'
    )

    property_id = fields.Many2one(
        'pms.property',
        string='Property',
        required=True,
        ondelete='restrict',
        index=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer / Signer',
        required=True,
        ondelete='restrict',
        index=True,
        help='The customer paying for the booking and legally responsible.'
    )

    guest_id = fields.Many2one(
        'res.partner',
        string='Guest',
        ondelete='restrict',
        index=True,
        help='The primary guest staying (defaults to the customer if left blank).'
    )

    checkin_date = fields.Date(
        string='Check-in Date',
        required=True,
        index=True
    )

    checkout_date = fields.Date(
        string='Check-out Date',
        required=True,
        index=True
    )

    number_of_guests = fields.Integer(
        string='Number of Guests',
        default=1,
        required=True
    )

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Linked Sales Order Line',
        ondelete='set null',
        copy=False
    )

    state = fields.Selection([
        ('draft', 'Draft / Enquiry'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, copy=False, tracking=True)

    number_of_nights = fields.Integer(
        string='Nights',
        compute='_compute_number_of_nights',
        store=True
    )

    total_price = fields.Float(
        string='Total Price',
        compute='_compute_total_price',
        store=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('pms.booking') or 'New'
            if not vals.get('guest_id') and vals.get('partner_id'):
                vals['guest_id'] = vals['partner_id']
        return super(PmsBooking, self).create(vals_list)

    def write(self, vals):
        if 'partner_id' in vals and 'guest_id' not in vals:
            for record in self:
                if not record.guest_id or record.guest_id == record.partner_id:
                    super(PmsBooking, record).write({'guest_id': vals['partner_id']})
        return super(PmsBooking, self).write(vals)

    @api.depends('checkin_date', 'checkout_date')
    def _compute_number_of_nights(self):
        for record in self:
            if record.checkin_date and record.checkout_date:
                if record.checkout_date > record.checkin_date:
                    record.number_of_nights = (record.checkout_date - record.checkin_date).days
                else:
                    record.number_of_nights = 0
            else:
                record.number_of_nights = 0

    @api.depends('number_of_nights', 'property_id', 'property_id.list_price')
    def _compute_total_price(self):
        for record in self:
            if record.property_id:
                record.total_price = record.number_of_nights * record.property_id.list_price
            else:
                record.total_price = 0.0

    @api.constrains('checkin_date', 'checkout_date')
    def _check_dates_validity(self):
        for record in self:
            if record.checkin_date and record.checkout_date:
                if record.checkin_date >= record.checkout_date:
                    raise ValidationError("Check-in date must be before the check-out date.")

    @api.constrains('property_id', 'checkin_date', 'checkout_date', 'state')
    def _check_overlapping_bookings(self):
        for record in self:
            if record.state in ['confirmed', 'checked_in'] and record.property_id:
                domain = [
                    ('property_id', '=', record.property_id.id),
                    ('state', 'in', ['confirmed', 'checked_in']),
                    ('id', '!=', record.id),
                    ('checkin_date', '<', record.checkout_date),
                    ('checkout_date', '>', record.checkin_date),
                ]
                overlaps = self.search(domain)
                if overlaps:
                    overlap_info = ", ".join(overlaps.mapped('name'))
                    raise ValidationError(
                        f"Double-booking Conflict: The property '{record.property_id.name}' is already "
                        f"booked during this period. Overlapping booking(s): {overlap_info}"
                    )

    # State transition actions
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_checkin(self):
        for record in self:
            if record.state != 'confirmed':
                raise ValidationError("Can only check in a confirmed booking.")
            record.write({'state': 'checked_in'})

    def action_checkout(self):
        for record in self:
            if record.state != 'checked_in':
                raise ValidationError("Can only check out a checked-in guest.")
            record.write({'state': 'checked_out'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
