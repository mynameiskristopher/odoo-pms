# -*- coding: utf-8 -*-
from odoo import models, fields

class PmsAmenity(models.Model):
    _name = 'pms.amenity'
    _description = 'Property Amenity'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Name of the amenity (e.g. Wi-Fi, Pool, Air Conditioning)'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of the amenity'
    )
