# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PmsProperty(models.Model):
    _name = 'pms.property'
    _description = 'Vacation Rental Property'
    _inherits = {'product.template': 'product_tmpl_id'}

    product_tmpl_id = fields.Many2one(
        'product.template',
        required=True,
        ondelete='cascade',
        string='Product Template',
        help='Linked product template'
    )

    override_config = fields.Boolean(
        string='Override Zone Configuration',
        default=False,
        help='Check to override zone configuration fields. If unchecked, fields are inherited from the zone.'
    )

    checkout_time = fields.Float(
        string='Checkout Time',
        compute='_compute_checkout_time',
        store=True,
        readonly=False,
        help='Latest checkout time'
    )
    
    checkin_time = fields.Float(
        string='Check-in Time',
        compute='_compute_checkin_time',
        store=True,
        readonly=False,
        help='Earliest check-in time'
    )
    
    pets_allowed = fields.Boolean(
        string='Pets Allowed',
        compute='_compute_pets_allowed',
        store=True,
        readonly=False,
        help='Whether pets are allowed in the rental property'
    )

    
    number_of_rooms = fields.Integer(
        string='Number of Rooms',
        default=1,
        help='Total number of rooms'
    )
    
    number_of_floors = fields.Integer(
        string='Number of Floors',
        default=1,
        help='Total number of floors'
    )
    
    square_footage = fields.Float(
        string='Square Footage',
        default=0.0,
        help='Total square footage of the property'
    )
    
    max_occupancy = fields.Integer(
        string='Max Occupancy',
        default=1,
        help='Maximum occupancy (number of guests)'
    )
    
    property_type = fields.Selection([
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('cabin', 'Cabin'),
        ('villa', 'Villa'),
    ], string='Property Type', required=True, default='house')
    
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='GPS Latitude'
    )
    
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='GPS Longitude'
    )

    short_name = fields.Char(
        string='Short Name',
        help='A shorter name for internal use or sync'
    )
    
    unit_code = fields.Char(
        string='Unit Code',
        help='Unique identifier code for the property unit'
    )
    
    headline = fields.Char(
        string='Headline',
        help='Catchy headline/tagline for marketing listings'
    )
    
    short_description = fields.Text(
        string='Short Description',
        help='Brief summary/teaser of the property'
    )
    
    directions = fields.Text(
        string='Directions',
        help='Access directions or instructions to reach the property'
    )
    
    street = fields.Char(
        string='Street Address'
    )
    
    street2 = fields.Char(
        string='Extended Address'
    )
    
    city = fields.Char(
        string='City'
    )
    
    state_id = fields.Many2one(
        'res.country.state',
        string='State',
        domain="[('country_id', '=?', country_id)]"
    )
    
    zip = fields.Char(
        string='Postal Code'
    )
    
    country_id = fields.Many2one(
        'res.country',
        string='Country'
    )
    
    full_bathrooms = fields.Integer(
        string='Full Bathrooms',
        default=0,
        help='Number of full bathrooms (toilet, sink, shower/tub)'
    )
    
    three_quarter_bathrooms = fields.Integer(
        string='3/4 Bathrooms',
        default=0,
        help='Number of three-quarter bathrooms (toilet, sink, shower)'
    )
    
    half_bathrooms = fields.Integer(
        string='Half Bathrooms',
        default=0,
        help='Number of half bathrooms (toilet, sink)'
    )
    
    bedrooms = fields.Integer(
        string='Bedrooms',
        default=0,
        help='Number of bedrooms'
    )
    
    municipality_id = fields.Char(
        string='Municipality ID',
        help='Local tax, permit, license, or municipality ID for STR compliance'
    )

    unit_owner_ids = fields.One2many(
        'pms.unit.owner',
        'unit_id',
        string='Owner History',
        help='Ownership records linking this unit to its owner(s).',
    )

    zone_id = fields.Many2one(
        'pms.zone',
        string='Zone',
        ondelete='restrict',
        index=True,
        help='The zone this property belongs to (e.g. Building A, Floor 2).'
    )

    custom_amenity_ids = fields.Many2many(
        'pms.amenity',
        'pms_property_amenity_rel',
        'property_id',
        'amenity_id',
        string='Custom Amenities',
        help='Amenities defined specifically for this property.'
    )
    override_amenities = fields.Boolean(
        string='Override Zone Amenities',
        default=False,
        help='Check to override zone amenities. If unchecked, zone amenities are inherited.'
    )
    amenity_ids = fields.Many2many(
        'pms.amenity',
        'pms_property_effective_amenity_rel',
        'property_id',
        'amenity_id',
        string='Amenities',
        compute='_compute_amenity_ids',
        store=True,
        help='Effective amenities (either inherited or overridden).'
    )

    @api.depends('override_config', 'zone_id.effective_checkin_time')
    def _compute_checkin_time(self):
        for prop in self:
            if not prop.override_config and prop.zone_id:
                prop.checkin_time = prop.zone_id.effective_checkin_time
            else:
                prop.checkin_time = prop.checkin_time or 0.0

    @api.depends('override_config', 'zone_id.effective_checkout_time')
    def _compute_checkout_time(self):
        for prop in self:
            if not prop.override_config and prop.zone_id:
                prop.checkout_time = prop.zone_id.effective_checkout_time
            else:
                prop.checkout_time = prop.checkout_time or 0.0

    @api.depends('override_config', 'zone_id.effective_pets_allowed')
    def _compute_pets_allowed(self):
        for prop in self:
            if not prop.override_config and prop.zone_id:
                prop.pets_allowed = prop.zone_id.effective_pets_allowed
            else:
                prop.pets_allowed = prop.pets_allowed or False

    @api.depends('custom_amenity_ids', 'override_amenities', 'zone_id.amenity_ids')
    def _compute_amenity_ids(self):
        for prop in self:
            if prop.override_amenities or not prop.zone_id:
                prop.amenity_ids = prop.custom_amenity_ids
            else:
                prop.amenity_ids = prop.zone_id.amenity_ids


