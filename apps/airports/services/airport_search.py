from django.db.models import Case, IntegerField, Q, QuerySet, Value, When

from common.utilities import normalize_arabic, normalize_latin


class AirportSearchService:
    """Ranked lookup for the departure/arrival picker.

    Two things a plain `icontains` gets wrong. Someone typing "DMM" wants
    Dammam first, not every airport whose name happens to contain those
    letters — so matches are scored and the score drives the ordering. And
    someone typing "اسطنبول" means إسطنبول — so the Arabic side matches against
    the folded columns the model maintains, not the stored spelling. The Latin
    side is folded for the same reason: the catalogue says Málaga and İzmir,
    and nobody types the accents.
    """

    # Lower sorts first.
    RANK_CODE = 0
    RANK_CITY_PREFIX = 1
    RANK_CITY = 2
    RANK_OTHER = 3

    @staticmethod
    def search(queryset: QuerySet, term: str) -> QuerySet:
        term = (term or "").strip()
        if not term:
            return queryset

        arabic = normalize_arabic(term)
        latin = normalize_latin(term)

        matches = (
            Q(iata_code__icontains=term)
            | Q(city_en_folded__icontains=latin)
            | Q(text_en_folded__icontains=latin)
            | Q(city_ar_folded__icontains=arabic)
            | Q(text_ar_folded__icontains=arabic)
        )

        rank = Case(
            When(iata_code__iexact=term, then=Value(AirportSearchService.RANK_CODE)),
            When(
                city_en_folded__istartswith=latin,
                then=Value(AirportSearchService.RANK_CITY_PREFIX),
            ),
            When(
                city_ar_folded__istartswith=arabic,
                then=Value(AirportSearchService.RANK_CITY_PREFIX),
            ),
            When(city_en_folded__icontains=latin, then=Value(AirportSearchService.RANK_CITY)),
            When(city_ar_folded__icontains=arabic, then=Value(AirportSearchService.RANK_CITY)),
            default=Value(AirportSearchService.RANK_OTHER),
            output_field=IntegerField(),
        )

        # `is_popular` breaks ties within a rank: two airports called Dubai are
        # both right, and the busier one is the better first guess.
        return (
            queryset.filter(matches)
            .annotate(match_rank=rank)
            .order_by("match_rank", "-is_popular", "order", "city_en")
        )
