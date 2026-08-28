from django.db.models import Case, IntegerField, Q, QuerySet, Value, When

from common.utilities import normalize_arabic


class AirportSearchService:
    """Ranked lookup for the departure/arrival picker.

    Two things a plain `icontains` gets wrong. Someone typing "DMM" wants
    Dammam first, not every airport whose name happens to contain those
    letters — so matches are scored and the score drives the ordering. And
    someone typing "اسطنبول" means إسطنبول — so the Arabic side matches against
    the folded columns the model maintains, not the stored spelling.
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

        # English needs no folding: icontains already case-folds it.
        folded = normalize_arabic(term)

        matches = (
            Q(iata_code__icontains=term)
            | Q(city_en__icontains=term)
            | Q(name_en__icontains=term)
            | Q(country_en__icontains=term)
            | Q(city_ar_folded__icontains=folded)
            | Q(text_ar_folded__icontains=folded)
        )

        rank = Case(
            When(iata_code__iexact=term, then=Value(AirportSearchService.RANK_CODE)),
            When(city_en__istartswith=term, then=Value(AirportSearchService.RANK_CITY_PREFIX)),
            When(
                city_ar_folded__istartswith=folded,
                then=Value(AirportSearchService.RANK_CITY_PREFIX),
            ),
            When(city_en__icontains=term, then=Value(AirportSearchService.RANK_CITY)),
            When(city_ar_folded__icontains=folded, then=Value(AirportSearchService.RANK_CITY)),
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
