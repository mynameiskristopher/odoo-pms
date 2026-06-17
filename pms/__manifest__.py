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
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pms_property_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
