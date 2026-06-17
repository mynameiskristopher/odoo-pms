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
