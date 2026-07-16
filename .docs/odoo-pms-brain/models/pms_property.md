# Model: `pms.property` (Vacation Rental)

This model represents a rentable property in the Property Management System (PMS), specifically aligned with the vacation rental domain.

## Schema.org Mapping

The `pms.property` model maps directly to Schema.org's **`VacationRental`** class, which is a subclass of **`LodgingBusiness`**.

| Schema.org Property | Odoo Field Name | Odoo Type | Description |
|---------------------|-----------------|-----------|-------------|
| - | `product_tmpl_id` | `Many2one` | Pointer to the delegated `product.template` (Odoo core) |
| `checkoutTime` | `checkout_time` | `Float` | The latest checkout time (represented as float, e.g. 11.0 for 11:00 AM) |
| `checkinTime` | `checkin_time` | `Float` | The earliest checkin time (represented as float, e.g. 15.0 for 3:00 PM) |
| `petsAllowed` | `pets_allowed` | `Boolean` | Indicates whether pets are allowed in the rental |
| `numberOfRooms` | `number_of_rooms`| `Integer` | Total number of rooms in the property |
| `numberOfFloors` | `number_of_floors`| `Integer` | Total number of floors in the property |
| `floorSize` | `square_footage` | `Float` | Total square footage of the property |
| `occupancy` | `max_occupancy` | `Integer` | Maximum number of guests allowed |
| `lodgingType` / Type| `property_type` | `Selection` | Category of property (house, apartment, cabin, villa) |
| `geo` (latitude) | `latitude` | `Float` | Latitude coordinate |
| `geo` (longitude) | `longitude` | `Float` | Longitude coordinate |
| `alternateName` | `short_name` | `Char` | A shorter name for internal use or sync |
| `identifier` | `unit_code` | `Char` | Unique identifier code for the property unit |
| `slogan` | `headline` | `Char` | Catchy headline/tagline for marketing listings |
| `description` (teaser) | `short_description` | `Text` | Brief summary/teaser of the property |
| - | `directions` | `Text` | Access directions or instructions to reach the property |
| `address.streetAddress` | `street` | `Char` | Street Address |
| `address.streetAddress` (ext) | `street2` | `Char` | Extended Address |
| `address.addressLocality` | `city` | `Char` | City |
| `address.addressRegion` | `state_id` | `Many2one` | State (references `res.country.state`) |
| `address.postalCode` | `zip` | `Char` | Postal Code (ZIP) |
| `address.addressCountry` | `country_id` | `Many2one` | Country (references `res.country`) |
| `numberOfBathroomsTotal` (full) | `full_bathrooms` | `Integer` | Number of full bathrooms (toilet, sink, shower/tub) |
| `numberOfBathroomsTotal` (3/4) | `three_quarter_bathrooms` | `Integer` | Number of three-quarter bathrooms (toilet, sink, shower) |
| `numberOfBathroomsTotal` (half) | `half_bathrooms` | `Integer` | Number of half bathrooms (toilet, sink) |
| `numberOfBedrooms` | `bedrooms` | `Integer` | Number of bedrooms |
| `permitNo` | `municipality_id` | `Char` | Local municipality ID, license, or permit |
| - | `zone_id` | `Many2one` | The taxonomical zone this property belongs to (references `pms.zone`) |



## Inheritance Design Decision: Delegation Inheritance (`_inherits`)

To represent a vacation rental property, we have chosen **delegation inheritance (`_inherits`)** over standard class extension (`_inherit`).

### Why Delegation Inheritance?

1. **Clean Database Separation**: Vacation rental-specific fields (e.g. checkin/checkout times, latitude, longitude) only apply to properties. Standard class extension (`_inherit`) would add these columns directly to the `product_template` table, polluting it for other product types.
2. **Polymorphic Product Representation**: Odoo's core sales, e-commerce, and invoicing systems depend on `product.template` and `product.product`. By utilizing delegation inheritance, a `pms.property` record automatically instantiates and links to an underlying `product.template` record.
3. **Seamless Integration**: This allows properties to be bought, sold, invoiced, or displayed on the website just like standard product templates, while retaining their unique rental attributes in a separate, dedicated table (`pms_property`).
