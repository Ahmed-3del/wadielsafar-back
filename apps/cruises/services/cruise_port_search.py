from django.db.models import Case, IntegerField, Q, QuerySet, Value, When

from common.utilities import normalize_arabic, normalize_latin


class CruisePortSearchService:
    """Ranked lookup for the cruise search's port picker.

    The same two problems the airport picker has. Someone typing "Dubai" wants
    Port Rashid first, not every port whose blurb mentions Dubai — so matches
    are scored and the score drives the order. And someone typing "اسطنبول"
    means إسطنبول, so the Arabic side matches the folded columns the model
    maintains rather than the stored spelling. The Latin side is folded for the
    same reason — the catalogue says Kuşadası, and nobody types the ş.
    """

    RANK_CITY_PREFIX = 0
    RANK_CITY = 1
    RANK_OTHER = 2

    @staticmethod
    def search(queryset: QuerySet, term: str) -> QuerySet:
        term = (term or "").strip()
        if not term:
            return queryset

        arabic = normalize_arabic(term)
        latin = normalize_latin(term)

        matches = (
            Q(city_en_folded__icontains=latin)
            | Q(text_en_folded__icontains=latin)
            | Q(city_ar_folded__icontains=arabic)
            | Q(text_ar_folded__icontains=arabic)
        )

        rank = Case(
            When(
                city_en_folded__istartswith=latin,
                then=Value(CruisePortSearchService.RANK_CITY_PREFIX),
            ),
            When(
                city_ar_folded__istartswith=arabic,
                then=Value(CruisePortSearchService.RANK_CITY_PREFIX),
            ),
            When(city_en_folded__icontains=latin, then=Value(CruisePortSearchService.RANK_CITY)),
            When(city_ar_folded__icontains=arabic, then=Value(CruisePortSearchService.RANK_CITY)),
            default=Value(CruisePortSearchService.RANK_OTHER),
            output_field=IntegerField(),
        )

        return queryset.filter(matches).annotate(match_rank=rank).order_by("match_rank", "order")
