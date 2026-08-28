import factory

from apps.flights.models import FlightDeal


class FlightDealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FlightDeal

    title_ar = factory.Sequence(lambda n: f"عرض رحلة {n}")
    title_en = factory.Sequence(lambda n: f"Flight Deal {n}")
    origin_city_ar = "الرياض"
    origin_city_en = "Riyadh"
    origin_airport_code = "RUH"
    destination_city_ar = "دبي"
    destination_city_en = "Dubai"
    destination_airport_code = "DXB"
    airline_name_en = "Saudia"
    trip_type = "ROUND_TRIP"
    cabin_class = "ECONOMY"
    price_from = "1200.00"
    is_active = True
