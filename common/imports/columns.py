"""What each resource's import sheet asks for.

Gathered here rather than scattered over eleven viewsets so the wording stays
consistent — every `help` line is what an agent reads in the template's second
sheet, and it is the only instruction they get.

A column is:
    name      the header in the spreadsheet
    field     the serializer's name for it, when the header should read
              differently — "destination" in the sheet, "destination_id" to the
              API, because nobody filling in a sheet has an id
    required  marked with * in the template; enforced by the serializer
    type      "boolean" or "list" for the cells that need coaxing
    help      one line, in the template
"""

from apps.flights.models import CabinClassChoices, TripTypeChoices
from apps.services.models import ServiceIconChoices
from common.constants import ServiceTypeChoices, VisaEntryChoices, VisaPurposeChoices


def text(name, help_text, *, required=False, field=None):
    column = {"name": name, "help": help_text, "required": required}
    if field:
        column["field"] = field
    return column


def flag(name, help_text):
    return {"name": name, "help": help_text, "type": "boolean"}


def ref(name, help_text, *, required=False, field=None):
    return text(name, help_text, required=required, field=field or f"{name}_id")


def choice(name, choices, help_text="", *, required=False, field=None):
    """A column whose value has to be one of a fixed set — read from the
    model's own `TextChoices`, not typed out by hand in this file.

    Hand-typing the list is exactly how this drifted: the visa import once
    told an agent to type TOURIST, WORK, TRANSIT, MEDICAL or FAMILY — four of
    which `VisaPurposeChoices` has never accepted — while never mentioning
    OTHER, which it does. A whole sheet of visas failed, and the serializer
    was never wrong: only what an agent was told to type into the sheet was,
    a comment away from the model and nothing to keep the two in step.
    Reading the list from the enum means this file cannot say something the
    model does not — a value added or renamed here shows up in the next
    template without anyone remembering to change this file too.
    """
    values = ", ".join(choices.values)
    # "A, B, C or D." rather than an Oxford comma before the last one, to
    # match every other list already written this way in this file.
    parts = values.rsplit(", ", 1)
    listed = " or ".join(parts) if len(parts) == 2 else values
    sentence = f"{listed}."
    if help_text:
        sentence = f"{sentence} {help_text}"
    return text(name, sentence, required=required, field=field)


BILINGUAL = "Arabic and English are separate columns; both are shown to visitors."

AIRPORT_COLUMNS = [
    text("iata_code", "The three-letter code, e.g. JED. This is what rows are matched on.", required=True),
    text("name_en", "Airport name in English.", required=True),
    text("name_ar", "Airport name in Arabic.", required=True),
    text("city_en", "City in English.", required=True),
    text("city_ar", "City in Arabic.", required=True),
    text("country_en", "Country in English. Spell it the same way across every row.", required=True),
    text("country_ar", "Country in Arabic.", required=True),
    text("country_code", "Two-letter ISO code, e.g. SA. Draws the flag."),
    flag("is_popular", "Offered before the traveller types anything."),
    flag("is_active", "No hides it from the pickers without deleting it."),
    text("order", "Lower numbers come first."),
]

CRUISE_PORT_COLUMNS = [
    text("code", "A short slug, e.g. jeddah. This is what rows are matched on.", required=True),
    text("name_en", "The port itself in English, e.g. Port of Barcelona.", required=True),
    text("name_ar", "The port in Arabic.", required=True),
    text("city_en", "City in English.", required=True),
    text("city_ar", "City in Arabic.", required=True),
    text("country_en", "Country in English. The cruise search groups ports by this.", required=True),
    text("country_ar", "Country in Arabic.", required=True),
    text("country_code", "Two-letter ISO code, e.g. IT."),
    flag("is_popular", "Offered before anyone types."),
    flag("is_active", "No hides it from the pickers."),
    text("order", "Lower numbers come first."),
]

CRUISE_COLUMNS = [
    text("title_en", "The cruise's name in English. Rows are matched on this.", required=True),
    text("title_ar", "The cruise's name in Arabic.", required=True),
    text("cruise_line_en", "Operator in English."),
    text("cruise_line_ar", "Operator in Arabic."),
    ref("destination", "The destination's English name, exactly as it is in Destinations."),
    ref("departure_port", "The port's code or English city, from Cruise ports.", field="departure_port_id"),
    text("departure_port_en", "Free-text port name, if it is not in the port list."),
    text("departure_port_ar", "The same in Arabic."),
    text("departure_date", "yyyy-mm-dd."),
    text("duration_nights", "A whole number of nights."),
    text("price_from", "Starting price per person, digits only.", required=True),
    text("currency", "Three letters, e.g. SAR. Defaults to SAR."),
    text("description_en", "Shown on the cruise page."),
    text("description_ar", "The same in Arabic."),
    text("included_services_en", "What the fare covers, one per line."),
    text("included_services_ar", "The same in Arabic."),
    text("cover_image", "A full https:// image URL."),
    flag("is_featured", "Yes puts it on the homepage rail."),
    flag("is_active", "No hides it from the website."),
]

HOTEL_COLUMNS = [
    text("name_en", "Hotel name in English. Rows are matched on this.", required=True),
    text("name_ar", "Hotel name in Arabic.", required=True),
    ref("destination", "The destination's English name, exactly as it is in Destinations.", required=True),
    text("star_rating", "1 to 5.", required=True),
    text("price_per_night_from", "Starting nightly rate, digits only.", required=True),
    text("currency", "Three letters, e.g. SAR."),
    text("address_en", "Street address in English."),
    text("address_ar", "Street address in Arabic."),
    text("description_en", "Shown on the hotel page."),
    text("description_ar", "The same in Arabic."),
    {"name": "amenities", "field": "amenity_ids", "type": "list",
     "help": "Amenity names in English, separated by commas. Each must already exist."},
    text("check_in_time", "HH:MM, e.g. 15:00."),
    text("check_out_time", "HH:MM, e.g. 12:00."),
    text("cover_image", "A full https:// image URL."),
    flag("is_featured", "Yes puts it on the homepage."),
    flag("is_active", "No hides it from the website."),
]

FLIGHT_COLUMNS = [
    text("title_en", "The deal's name in English. Rows are matched on this.", required=True),
    text("title_ar", "The deal's name in Arabic.", required=True),
    text("origin_airport_code", "Three-letter IATA code, e.g. JED.", required=True),
    text("origin_city_en", "Departure city in English.", required=True),
    text("origin_city_ar", "Departure city in Arabic.", required=True),
    text("destination_airport_code", "Three-letter IATA code, e.g. DXB.", required=True),
    text("destination_city_en", "Arrival city in English.", required=True),
    text("destination_city_ar", "Arrival city in Arabic.", required=True),
    text("price_from", "Starting fare, digits only.", required=True),
    text("currency", "Three letters, e.g. SAR."),
    text("airline_name_en", "Airline in English."),
    text("airline_name_ar", "Airline in Arabic."),
    text("airline_logo", "A full https:// image URL."),
    choice("trip_type", TripTypeChoices),
    choice("cabin_class", CabinClassChoices),
    text("departure_date", "yyyy-mm-dd."),
    text("return_date", "yyyy-mm-dd. Leave blank on a one-way."),
    text("baggage_allowance_kg", "A whole number of kilos."),
    flag("is_featured", "Yes puts it on the homepage."),
    flag("is_active", "No hides it from the website."),
]

VISA_COUNTRY_COLUMNS = [
    text("name_en", "Country in English. Rows are matched on this.", required=True),
    text("name_ar", "Country in Arabic.", required=True),
    text("flag_image", "A full https:// image URL for the flag."),
    text("cover_image", "A full https:// photo URL for the card."),
    flag("is_active", "No hides it from the website."),
]

VISA_TYPE_COLUMNS = [
    ref("country", "The visa country's English name, exactly as it is in Visa countries.", required=True),
    text("name_en", "The visa in English, e.g. Tourist Visa. Matched together with the country.", required=True),
    text("name_ar", "The visa in Arabic.", required=True),
    text("price", "Digits only.", required=True),
    text("processing_time_days", "A whole number of days.", required=True),
    text("validity_days", "How long it stays valid, in days."),
    choice("purpose", VisaPurposeChoices, "Leave blank and it shows under every purpose instead of one."),
    choice("entry_type", VisaEntryChoices, "Leave blank where it varies by applicant."),
    text("requirements_en", "What the applicant must provide, one per line."),
    text("requirements_ar", "The same in Arabic."),
    text("cover_image", "A full https:// image URL."),
    flag("is_active", "No hides it from the website."),
]

DESTINATION_COLUMNS = [
    text("name_en", "Destination in English. Rows are matched on this.", required=True),
    text("name_ar", "Destination in Arabic.", required=True),
    text("country_en", "Country in English.", required=True),
    text("country_ar", "Country in Arabic.", required=True),
    text("description_en", "Shown on the destination page."),
    text("description_ar", "The same in Arabic."),
    text("cover_image", "A full https:// image URL."),
    text("order", "Lower numbers come first."),
    flag("is_active", "No hides it from the website."),
]

PACKAGE_COLUMNS = [
    text("title_en", "The package in English. Rows are matched on this.", required=True),
    text("title_ar", "The package in Arabic.", required=True),
    ref("category", "The category's English name, exactly as it is in the panel.", required=True),
    ref("destination", "The destination's English name.", required=True),
    text("price_from", "Starting price per person, digits only.", required=True),
    text("duration_days", "A whole number of days."),
    text("description_en", "Shown on the package page."),
    text("description_ar", "The same in Arabic."),
    text("included_services_en", "What the price covers, one per line."),
    text("included_services_ar", "The same in Arabic."),
    text("cover_image", "A full https:// image URL."),
    flag("is_featured", "Yes puts it on the homepage."),
    flag("is_active", "No hides it from the website."),
]

OFFER_COLUMNS = [
    text("title_en", "The offer in English. Rows are matched on this.", required=True),
    text("title_ar", "The offer in Arabic.", required=True),
    choice("service_type", ServiceTypeChoices, required=True),
    text("starts_at", "yyyy-mm-dd.", required=True),
    text("ends_at", "yyyy-mm-dd. The offer disappears from the website after this.", required=True),
    text("price_before", "The old price, digits only. Leave blank for 'price on request'."),
    text("price_after", "The offer price. The discount is worked out from the pair."),
    text("description_en", "Shown on the offer page."),
    text("description_ar", "The same in Arabic."),
    text("image", "A full https:// image URL."),
    flag("is_featured", "Yes puts it on the homepage."),
    flag("is_active", "No hides it from the website."),
]

SERVICE_COLUMNS = [
    text("name_en", "The service in English. Rows are matched on this.", required=True),
    text("name_ar", "The service in Arabic.", required=True),
    text("description_en", "One line, shown on the tile."),
    text("description_ar", "The same in Arabic."),
    choice("icon", ServiceIconChoices),
    text("link", "Where the tile leads, as a path on this site, e.g. /visas. Blank means the contact form."),
    choice("service_type", ServiceTypeChoices, "What the contact form opens on."),
    text("image", "A full https:// image URL."),
    text("order", "Lower numbers come first."),
    flag("is_active", "No hides it from the website."),
]
