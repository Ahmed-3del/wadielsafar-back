import factory

from apps.airports.models import Airport


class AirportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Airport

    # A rolling synthetic code so a test can make as many as it likes without
    # colliding with the shipped catalogue.
    iata_code = factory.Sequence(lambda n: f"Z{n % 10}{chr(65 + n // 10 % 26)}")
    name_ar = factory.Sequence(lambda n: f"مطار {n}")
    name_en = factory.Sequence(lambda n: f"Airport {n}")
    city_ar = factory.Sequence(lambda n: f"مدينة {n}")
    city_en = factory.Sequence(lambda n: f"City {n}")
    country_ar = "دولة"
    country_en = "Country"
    country_code = "XX"
    is_active = True
