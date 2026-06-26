# Model: `pms.unit.owner` (Unit Ownership)

This model creates a relationship between an owner and a property/unit, tracking contracts, dates, and fractional ownership.

## Schema Layout

| Field Name | Type | Description |
|------------|------|-------------|
| `owner_id` | `Many2one('pms.owner')` | The owner for the unit (required, restrict delete). |
| `unit_id` | `Many2one('pms.property')` | The property/unit the owner owns (required, cascade delete). |
| `contract_id` | `Integer` | Contract ID attached to this ownership (required). |
| `tax_mode` | `Selection` | `inclusive`, `exclusive`, or `none` (required, default `exclusive`). |
| `start_date` | `Date` | Ownership start date (required, indexed). |
| `end_date` | `Date` | Ownership end date (indexed). |
| `owner_name` | `Char` | Computed via `related='owner_id.name'`, stored. |
| `unit_name` | `Char` | Computed via `related='unit_id.name'`, stored. |

## Constraints

- **Date validation**: `end_date` must be ≥ `start_date` if both are set.

## Relationships

- `pms.owner` → `unit_owner_ids` (One2many reverse from owner side)
- `pms.property` → `unit_owner_ids` (One2many reverse from property side, added to PmsProperty model)
- Both sides can see ownership records in their respective form views.

## Design Decisions

1. **`contract_id` as Integer, not Many2one**: The contract model doesn't exist yet in this module. Stored as a plain integer ID for future integration.
2. **No `contract_type` field**: Removed — fractional ownership is not part of the current model scope. Only standard ownership is supported.
3. **No `fractional_inventory_id` field**: Removed — fractional ownership was removed from scope entirely.
4. **Related fields for display**: `owner_name` and `unit_name` use `related=` with `store=True` for efficient list view display without joins.
5. **`_order = 'start_date desc, id desc'`**: Most recent ownership records appear first.