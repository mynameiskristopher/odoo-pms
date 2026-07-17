# -*- coding: utf-8 -*-
{
    'name': 'Property Management System',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'Vacation Rental Property Management System',
    'description': """
Property Management System
==========================
This module adds support for managing vacation rental properties,
mapping directly to Schema.org/VacationRental entities and integrating
seamlessly with Odoo's product templates.
    """,
    'author': 'Antigravity',
    'depends': [
        'base',
        'product',
        'sale',
        'mail',
        'analytic',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/pms_orm_data.xml',
        'views/pms_property_views.xml',
        'views/pms_zone_views.xml',
        'views/pms_booking_views.xml',
        'views/pms_owner_views.xml',
        'views/pms_owner_lead_views.xml',
        'views/pms_unit_owner_views.xml',
        'views/pms_charge_type_views.xml',
        'views/pms_revenue_policy_views.xml',
        'views/pms_owner_agreement_views.xml',
        'views/pms_reservation_charge_views.xml',
        'views/pms_owner_settlement_views.xml',
        'security/ir.sequence_pms_revenue.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
