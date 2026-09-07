"""Latin text folding for search.

The airport catalogue is not written in the alphabet people type on. It says
Málaga, İzmir, Ålesund, Asunción, Đà Nẵng — and a traveller looking for any of
them types malaga, izmir, alesund, asuncion, da nang. `icontains` case-folds
but does not strip accents, so before this existed those airports were in the
database and unreachable from the search box.

The same idea as the Arabic folding next door, and used the same way: both the
stored text and the search term are folded, the folded copy is only ever
matched against, and it is never displayed.
"""

import unicodedata

# Letters that carry their difference in the letter itself rather than in a
# combining mark, so decomposition alone leaves them unchanged. Turkish is the
# one that bites hardest: "İzmir" lower-cases to "i̇zmir" with a stray dot, and
# the "ı" in "Adıyaman" is not the "i" anyone types.
_FOLD = str.maketrans(
    {
        "ø": "o", "Ø": "o",
        "đ": "d", "Đ": "d",
        "ð": "d", "Ð": "d",
        "ł": "l", "Ł": "l",
        "ı": "i", "İ": "i",
        "þ": "th", "Þ": "th",
        "ß": "ss",
        "æ": "ae", "Æ": "ae",
        "œ": "oe", "Œ": "oe",
        "ŋ": "n", "Ŋ": "n",
        "ʻ": "", "ʼ": "", "'": "", "’": "",
    }
)


def normalize_latin(text: str) -> str:
    """Fold `text` to the form used for matching. Safe on non-Latin input.

    Arabic passes through untouched — its own folding is a separate step, and
    running both over one string is how you end up with neither.
    """
    if not text:
        return ""
    # NFD splits "á" into "a" + a combining acute, which the category filter
    # then drops. Anything with no decomposition is handled by the table above.
    decomposed = unicodedata.normalize("NFD", text.translate(_FOLD))
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return " ".join(stripped.casefold().split())
