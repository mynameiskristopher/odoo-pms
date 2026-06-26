# Model: `pms.zone.type` (Zone Type)

This model defines customizable zone classifications such as "Region", "Building", or "Floor".

## Schema

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `Char` | Name of the type (e.g., "Region", "Building", "Floor") |
| `code` | `Char` | Optional short code representing this type |
| `description` | `Text` | Description explaining the intended usage of this type |
