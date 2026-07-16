# Model: `pms.zone` (Zone)

This model represents a hierarchical taxonomic zone (e.g., Region, Building, Floor) where properties can be classified.

## Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `Char` | Name of the zone (e.g., "Floor 2") |
| `complete_name` | `Char` | Stored, computed recursive path name (e.g. "North Region / Building A / Floor 2") |
| `type_id` | `Many2one` | Type classification (references `pms.zone.type`, required, restrict) |
| `parent_id` | `Many2one` | Parent Zone in the hierarchy (references `pms.zone`, cascade, indexed) |
| `child_ids` | `One2many` | Child Zones under this zone |
| `property_ids` | `One2many` | Properties inside this zone |
| `active` | `Boolean` | Flag indicating active status (defaults to True) |
| `custom_amenity_ids` | `Many2many` | Custom amenities defined explicitly on this zone (references `pms.amenity`) |
| `override_amenities` | `Boolean` | Flag indicating whether this zone overrides parent amenities instead of inheriting them |
| `amenity_ids` | `Many2many` | Effective resolved amenities for this zone (computed, stored, recursive) |
| `checkin_time` | `Float` | Check-in time override (0.0 to inherit from parent) |
| `checkout_time` | `Float` | Checkout time override (0.0 to inherit from parent) |
| `pets_allowed` | `Selection` | Pets allowed setting override (`yes`, `no`, `inherit`) |
| `effective_checkin_time` | `Float` | Effective check-in time after applying inheritance (computed, stored, recursive) |
| `effective_checkout_time` | `Float` | Effective checkout time after applying inheritance (computed, stored, recursive) |
| `effective_pets_allowed` | `Boolean` | Effective pets allowed flag after applying inheritance (computed, stored, recursive) |

## Hierarchy Design

We utilize Odoo's native hierarchy support:
- `_parent_store = True` to optimize recursive child/parent database queries.
- `parent_path` indexed char field storing parent path hierarchies.
- Stored, computed `complete_name` combining parent names with `/` separators. This field is designated as the `_rec_name` for easy selection and lookup across Odoo.

### Configuration & Amenities Inheritance

To reduce administrative overhead, child zones automatically inherit configurations and amenities from their parent zones:
1. **Amenities Inheritance**: 
   - If `override_amenities` is `False`, `amenity_ids` is computed as equal to the parent zone's `amenity_ids`.
   - If `override_amenities` is `True`, `amenity_ids` is computed as equal to this zone's `custom_amenity_ids` (which can be empty).
2. **Field Configuration Inheritance**:
   - `effective_checkin_time` / `effective_checkout_time`: If the override value is set (i.e. `> 0.0`), it is used. Otherwise, the parent's `effective_checkin_time` / `effective_checkout_time` is inherited recursively.
   - `effective_pets_allowed`: Resolves to `True` if `pets_allowed` is `'yes'`, `False` if `'no'`, and inherits the parent's `effective_pets_allowed` if set to `'inherit'`.

