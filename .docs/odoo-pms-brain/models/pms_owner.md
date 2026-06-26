# Model: `pms.owner` (Property Owner)

This model represents a property owner (company or individual) in the PMS. Owners are linked to rental units via `pms.unit.owner`.

## Inheritance

- `_inherit = ['mail.thread']` — provides chatter/followers support on the owner form.

## Schema Layout

| Field Name | Type | Description |
|------------|------|-------------|
| `owner_type` | `Selection` | Type of owner. Currently only `('owner', 'Owner')`. |
| `active` | `Boolean` | Built-in Odoo active/archive field (replaces custom `is_active`). |
| `name` | `Char` | Company/individual name (required). |
| `street_address` | `Char` | Business street address. |
| `extended_address` | `Char` | Extended address (apt, suite). |
| `locality` | `Char` | City/locality. |
| `region` | `Char` | State/region. |
| `postal` | `Char` | Postal/ZIP code. |
| `country` | `Char` | ISO 3166-1 alpha-2 country code (2 chars). |
| `tax_type` | `Selection` | 1099 income classification: rents, other, none, non_employee_compensation. |
| `tax_name` | `Char` | 1099 tax payee name (required). |
| `tax_id` | `Char` | 1099 Tax ID (restricted to managers). |
| `ach_account_number` | `Char` | ACH account number (restricted). |
| `ach_routing_number` | `Char` | ACH routing number, exactly 9 digits (restricted). |
| `ach_account_type` | `Selection` | ACH account type: business-checking, business-savings, personal-checking, personal-savings (deprecated). |
| `ach_verified_at` | `Datetime` | When ACH was pre-noted (deprecated). |
| `payment_type` | `Selection` | print or direct (deprecated). |
| `gl_expiration_date` | `Date` | General liability insurance expiration (deprecated). |
| `gl_insurance_policy` | `Char` | GL insurance policy number (deprecated). |
| `wc_expiration_date` | `Date` | Workers comp expiration date (deprecated). |
| `wc_insurance_policy` | `Char` | WC insurance policy number (deprecated). |
| `travel_agent_deduct_commission` | `Boolean` | Enable travel agent commission deduction. |
| `travel_agent_commission` | `Float` | Commission % (0–100). |
| `travel_agent_iata_number` | `Char` | IATA number for travel agents. |
| `enable_work_order_approval` | `Boolean` | Allow vendor/owner to approve work orders. |
| `notes` | `Html` | Internal notes (rich text). |
| `website` | `Char` | Website URL. |
| `email` | `Char` | Email address. |
| `fax` | `Char` | Fax number (E.164 format). |
| `phone` | `Char` | Phone number (E.164 format). |
| `tag_ids` | `Many2many` | Tags via `pms.owner.tag`. |
| `tax_street_address` | `Char` | Tax address street (required). |
| `tax_extended_address` | `Char` | Tax address extended (required). |
| `tax_locality` | `Char` | Tax city (required). |
| `tax_region` | `Char` | Tax state/region (required). |
| `tax_postal_code` | `Char` | Tax postal code (required). |
| `tax_country` | `Char` | Tax country ISO 2-char code (required). |
| `tax_phone` | `Char` | Tax phone (required). |
| `company_id` | `Many2one` | Company (`res.company`), defaults to env company. |
| `always_show_in_statements` | `Boolean` | Always show in statements. |
| `split_with_contacts` | `Boolean` | Split with contacts. |
| `agent_commission` | `Char` | Agent commission. |
| `current_balance` | `Monetary` | Current financial balance. |
| `minimum_balance` | `Monetary` | Minimum balance. |
| `opening_balance` | `Monetary` | Opening balance (required, default 0). |
| `unit_owner_ids` | `One2many` | Ownership records linking to units (`pms.unit.owner`). |
| `currency_id` | `Many2one` | Computed currency from company for monetary widgets. |

## Constraints

- **Travel Agent Commission**: Must be between 0 and 100.
- **ACH Routing Number**: Must be exactly 9 digits if provided.
- **Country**: Must be 2-character ISO code if provided.
- **Tax Country**: Must be 2-character ISO code if provided.

## Key Design Decisions

1. **Built-in `active` field**: Uses Odoo's standard `active` field instead of a custom `is_active` boolean. This gives us free archive/unarchive behavior, `toggle_active` button, and automatic `active_test` filtering.
2. **No `contact_ids` One2many to `res.partner`**: Removed because `res.partner` doesn't have a `pms_owner_id` field. Owner contacts can be managed through Odoo's native partner system separately if needed.
3. **Built-in audit fields**: Relies on Odoo's magic fields (`create_date`, `create_uid`, `write_date`, `write_uid`) instead of custom timestamp fields.
4. **`mail.thread` inheritance**: Enables the Odoo chatter/message system on owner records.
5. **`_rec_name = 'name'`**: Ensures proper display names in Many2one dropdowns.