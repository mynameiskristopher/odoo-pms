# -*- coding: utf-8 -*-
from odoo import models, fields

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

    checkout_time = fields.Float(
        string='Checkout Time',
        help='Latest checkout time'
    )
    
    checkin_time = fields.Float(
        string='Check-in Time',
        help='Earliest check-in time'
    )
    
    pets_allowed = fields.Boolean(
        string='Pets Allowed',
        default=False,
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
