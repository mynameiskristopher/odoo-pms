# Model: `pms.booking` (Vacation Rental Booking)

This model represents a customer reservation for a vacation rental property, managing dates, guest details, and integrating with Odoo's sales modules.

## Schema Layout

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `Char` | Unique booking identifier generated on creation. |
| `property_id` | `Many2one` | Reference to the property model (`pms.property`). |
| `partner_id` | `Many2one` | Reference to `res.partner` - customer responsible for payment/contract. |
| `guest_id` | `Many2one` | Reference to `res.partner` - the guest staying (defaults to customer). |
| `checkin_date` | `Date` | Earliest check-in date. |
| `checkout_date` | `Date` | Latest check-out date. |
| `number_of_guests` | `Integer` | Count of guests staying. |
| `sale_line_id` | `Many2one` | Reference to `sale.order.line` that links this booking to sales. |
| `state` | `Selection` | Workflow state: `draft`, `confirmed`, `checked_in`, `checked_out`, `cancelled`. |
| `number_of_nights` | `Integer` | Computed: checkout_date - checkin_date. |
| `total_price` | `Float` | Computed: number_of_nights * property price. |

## Lifecycle States & Sales Order Sync

The booking lifecycle is synchronized with its linked sales order:
1. **Draft/Enquiry (`draft`)**: Created manually or from website enquiries.
2. **Confirmed (`confirmed`)**: Triggered automatically when the associated Odoo `sale.order` is confirmed (sent to sale).
3. **Checked-In (`checked_in`)**: Initiated manually by desk agent when the guest arrives.
4. **Checked-Out (`checked_out`)**: Initiated manually by desk agent upon guest departure.
5. **Cancelled (`cancelled`)**: Triggered automatically when the associated Odoo `sale.order` is cancelled.

## Overlap Validation (Double-Booking Prevention)

To maintain database integrity, a python constraint is executed on save/update:
- A booking cannot have overlapping check-in/check-out dates for the same property if it is in `confirmed` or `checked_in` states.
- Formula: `start_a < end_b AND end_a > start_b` for bookings on the same `property_id` where `id != self.id` and states are `confirmed` or `checked_in`.
- This constraint is designed to permit custom bypass flags in the future to allow administrator overriding (waitlists or overbooking).
