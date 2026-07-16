# Model: `pms.amenity` (Property Amenity)

This model represents a standard property amenity (e.g. WiFi, Pool, Air Conditioning) that can be associated with zones or properties.

## Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `Char` | Name of the amenity (e.g., "Wi-Fi", "Pool", "Air Conditioning") (Required) |
| `description` | `Text` | Detailed description of the amenity |

## Relationships

- **Zone Association (`custom_amenity_ids` / `amenity_ids` on `pms.zone`)**:
  - Associated via Many2many fields.
  - Used for defining amenities specifically for a zone or resolved recursively down the hierarchy.
- **Property Association (`custom_amenity_ids` / `amenity_ids` on `pms.property`)**:
  - Associated via Many2many fields.
  - Used for defining amenities specifically for a property or inheriting from its zone.
