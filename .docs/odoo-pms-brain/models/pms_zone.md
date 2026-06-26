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

## Hierarchy Design

We utilize Odoo's native hierarchy support:
- `_parent_store = True` to optimize recursive child/parent database queries.
- `parent_path` indexed char field storing parent path hierarchies.
- Stored, computed `complete_name` combining parent names with `/` separators. This field is designated as the `_rec_name` for easy selection and lookup across Odoo.
