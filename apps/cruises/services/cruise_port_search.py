from django.db.models import Case, IntegerField, Q, QuerySet, Value, When

from common.utilities import normalize_arabic


class CruisePortSearchService:
    """Ranked lookup for the cruise search's port picker.

    The same two problems the airport picker has. Someone typing "Dubai" wants
    Port Rashid first, not every port whose blurb mentions Dubai — so matches
    are scored and the score drives the order. And someone typing "اسطنبول"
    means إسطنبول, so the Arabic side matches the folded columns the model
    maintains rather than the stored spelling.
    """

    RANK_CITY_PREFIX = 0
    RANK_CITY = 1
    RANK_OTHER = 2

    @staticmethod
    def search(queryset: QuerySet, term: str) -> QuerySet:
        term = (term or "").strip()
        if not term:
            return queryset

        # English needs no folding: icontains already case-folds it.
        folded = normalize_arabic(term)

        matches = (
            Q(city_en__icontains=term)
            | Q(name_en__icontains=term)
            | Q(country_en__icontains=term)
            | Q(city_ar_folded__icontains=folded)
            | Q(text_ar_folded__icontains=folded)
        )

        rank = Case(
            When(city_en__istartswith=term, then=Value(CruisePortSearchService.RANK_CITY_PREFIX)),
            When(
                city_ar_folded__istartswith=folded,
                then=Value(CruisePortSearchService.RANK_CITY_PREFIX),
            ),
            When(city_en__icontains=term, then=Value(CruisePortSearchService.RANK_CITY)),
            When(city_ar_folded__icontains=folded, then=Value(CruisePortSearchService.RANK_CITY)),
            default=Value(CruisePortSearchService.RANK_OTHER),
            output_field=IntegerField(),
        )

        return queryset.filter(matches).annotate(match_rank=rank).order_by("match_rank", "order")
