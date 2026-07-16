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

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for zone in self:
            if zone.parent_id:
                zone.complete_name = '%s / %s' % (zone.parent_id.complete_name, zone.name)
            else:
                zone.complete_name = zone.name
