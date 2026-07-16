# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase

class TestZoneHierarchy(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create zone types
        cls.type_region = cls.env['pms.zone.type'].create({
            'name': 'Region',
            'code': 'REG'
        })
        cls.type_building = cls.env['pms.zone.type'].create({
            'name': 'Building',
            'code': 'BLD'
        })
        cls.type_floor = cls.env['pms.zone.type'].create({
            'name': 'Floor',
            'code': 'FLR'
        })

        # Create amenities
        cls.amenity_wifi = cls.env['pms.amenity'].create({'name': 'WiFi'})
        cls.amenity_pool = cls.env['pms.amenity'].create({'name': 'Pool'})
        cls.amenity_parking = cls.env['pms.amenity'].create({'name': 'Parking'})

    def test_zone_hierarchy_inheritance(self):
        # 1. Create Parent Zone
        parent_zone = self.env['pms.zone'].create({
            'name': 'North Region',
            'type_id': self.type_region.id,
            'checkin_time': 14.0,
            'checkout_time': 11.0,
            'pets_allowed': 'no',
            'custom_amenity_ids': [(6, 0, [self.amenity_wifi.id])],
            'override_amenities': True,
        })

        # Assert parent effective values
        self.assertEqual(parent_zone.effective_checkin_time, 14.0)
        self.assertEqual(parent_zone.effective_checkout_time, 11.0)
        self.assertFalse(parent_zone.effective_pets_allowed)
        self.assertEqual(parent_zone.amenity_ids, self.amenity_wifi)

        # 2. Create Child Zone (inheriting)
        child_zone = self.env['pms.zone'].create({
            'name': 'Building A',
            'type_id': self.type_building.id,
            'parent_id': parent_zone.id,
            'pets_allowed': 'inherit',
        })

        # Assert child effective values (all inherited)
        self.assertEqual(child_zone.effective_checkin_time, 14.0)
        self.assertEqual(child_zone.effective_checkout_time, 11.0)
        self.assertFalse(child_zone.effective_pets_allowed)
        self.assertEqual(child_zone.amenity_ids, self.amenity_wifi)

        # 3. Create Grandchild Zone (overriding some)
        grandchild_zone = self.env['pms.zone'].create({
            'name': 'Floor 1',
            'type_id': self.type_floor.id,
            'parent_id': child_zone.id,
            'checkin_time': 15.0,
            'pets_allowed': 'yes',
            'custom_amenity_ids': [(6, 0, [self.amenity_pool.id])],
            'override_amenities': True,
        })

        # Assert grandchild effective values (some overridden, checkout_time inherited)
        self.assertEqual(grandchild_zone.effective_checkin_time, 15.0)
        self.assertEqual(grandchild_zone.effective_checkout_time, 11.0)
        self.assertTrue(grandchild_zone.effective_pets_allowed)
        self.assertEqual(grandchild_zone.amenity_ids, self.amenity_pool)

        # 4. Create Property (inheriting from Grandchild Zone)
        property_inherit = self.env['pms.property'].create({
            'name': 'Room 101',
            'zone_id': grandchild_zone.id,
            'property_type': 'apartment',
        })

        # Assert property effective values are inherited from grandchild zone
        self.assertEqual(property_inherit.checkin_time, 15.0)
        self.assertEqual(property_inherit.checkout_time, 11.0)
        self.assertTrue(property_inherit.pets_allowed)
        self.assertEqual(property_inherit.amenity_ids, self.amenity_pool)

        # 5. Create Property (overriding values)
        property_override = self.env['pms.property'].create({
            'name': 'VIP Suite 102',
            'zone_id': grandchild_zone.id,
            'property_type': 'apartment',
            'override_config': True,
            'checkin_time': 16.0,
            'pets_allowed': False,
            'override_amenities': True,
            'custom_amenity_ids': [(6, 0, [self.amenity_wifi.id, self.amenity_parking.id])]
        })

        # Assert property overridden values
        self.assertEqual(property_override.checkin_time, 16.0)
        # Note: checkout_time was 0.0, and since override_config is True, it remains 0.0
        self.assertEqual(property_override.checkout_time, 0.0)
        self.assertFalse(property_override.pets_allowed)
        self.assertEqual(property_override.amenity_ids, self.amenity_wifi + self.amenity_parking)
