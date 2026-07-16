# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PmsZoneType(models.Model):
    _name = 'pms.zone.type'
    _description = 'Zone Type'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Name of the zone type (e.g. Region, Building, Floor)'
    )
    code = fields.Char(
        string='Code',
        help='Short code representing this zone type'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of this zone type'
    )


class PmsZone(models.Model):
    _name = 'pms.zone'
    _description = 'Zone'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Name of the zone'
    )
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        recursive=True,
        store=True,
        help='Full hierarchical name'
    )
    type_id = fields.Many2one(
        'pms.zone.type',
        string='Zone Type',
        required=True,
        ondelete='restrict',
        help='The type/classification of this zone'
    )
    parent_id = fields.Many2one(
        'pms.zone',
        string='Parent Zone',
        index=True,
        ondelete='cascade',
        help='Parent zone in the hierarchy'
    )
    child_ids = fields.One2many(
        'pms.zone',
        'parent_id',
        string='Child Zones'
    )
    parent_path = fields.Char(
        index=True
    )
    property_ids = fields.One2many(
        'pms.property',
        'zone_id',
        string='Properties'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set to false to hide this zone without deleting it.'
    )

    # Amenities Configuration and Inheritance
    custom_amenity_ids = fields.Many2many(
        'pms.amenity',
        'pms_zone_amenity_rel',
        'zone_id',
        'amenity_id',
        string='Custom Amenities',
        help='Amenities defined specifically for this zone.'
    )
    override_amenities = fields.Boolean(
        string='Override Parent Amenities',
        default=False,
        help='Check to override parent amenities. If unchecked, parent amenities are inherited.'
    )
    amenity_ids = fields.Many2many(
        'pms.amenity',
        'pms_zone_effective_amenity_rel',
        'zone_id',
        'amenity_id',
        string='Effective Amenities',
        compute='_compute_amenity_ids',
        store=True,
        recursive=True,
        help='Effective amenities (either inherited or overridden).'
    )

    # Configuration Fields & Override Settings
    checkin_time = fields.Float(
        string='Check-in Time Override',
        help='Earliest check-in time configured on this zone (leave 0.0 to inherit).'
    )
    checkout_time = fields.Float(
        string='Checkout Time Override',
        help='Latest checkout time configured on this zone (leave 0.0 to inherit).'
    )
    pets_allowed = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ('inherit', 'Inherit from Parent')
    ], string='Pets Allowed Override', default='inherit', help='Whether pets are allowed in this zone')

    # Effective/Inherited Values (Computed)
    effective_checkin_time = fields.Float(
        string='Effective Check-in Time',
        compute='_compute_effective_checkin_time',
        store=True,
        recursive=True,
        help='Resolved check-in time after applying hierarchy inheritance.'
    )
    effective_checkout_time = fields.Float(
        string='Effective Checkout Time',
        compute='_compute_effective_checkout_time',
        store=True,
        recursive=True,
        help='Resolved checkout time after applying hierarchy inheritance.'
    )
    effective_pets_allowed = fields.Boolean(
        string='Effective Pets Allowed',
        compute='_compute_effective_pets_allowed',
        store=True,
        recursive=True,
        help='Resolved pets allowed flag after applying hierarchy inheritance.'
    )

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for zone in self:
            if zone.parent_id:
                zone.complete_name = '%s / %s' % (zone.parent_id.complete_name, zone.name)
            else:
                zone.complete_name = zone.name

    @api.depends('custom_amenity_ids', 'override_amenities', 'parent_id.amenity_ids')
    def _compute_amenity_ids(self):
        for zone in self:
            if zone.override_amenities or not zone.parent_id:
                zone.amenity_ids = zone.custom_amenity_ids
            else:
                zone.amenity_ids = zone.parent_id.amenity_ids

    @api.depends('checkin_time', 'parent_id.effective_checkin_time')
    def _compute_effective_checkin_time(self):
        for zone in self:
            if zone.checkin_time > 0.0:
                zone.effective_checkin_time = zone.checkin_time
            elif zone.parent_id:
                zone.effective_checkin_time = zone.parent_id.effective_checkin_time
            else:
                zone.effective_checkin_time = 0.0

    @api.depends('checkout_time', 'parent_id.effective_checkout_time')
    def _compute_effective_checkout_time(self):
        for zone in self:
            if zone.checkout_time > 0.0:
                zone.effective_checkout_time = zone.checkout_time
            elif zone.parent_id:
                zone.effective_checkout_time = zone.parent_id.effective_checkout_time
            else:
                zone.effective_checkout_time = 0.0

    @api.depends('pets_allowed', 'parent_id.effective_pets_allowed')
    def _compute_effective_pets_allowed(self):
        for zone in self:
            if zone.pets_allowed == 'yes':
                zone.effective_pets_allowed = True
            elif zone.pets_allowed == 'no':
                zone.effective_pets_allowed = False
            elif zone.parent_id:
                zone.effective_pets_allowed = zone.parent_id.effective_pets_allowed
            else:
                zone.effective_pets_allowed = False

