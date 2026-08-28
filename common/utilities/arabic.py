"""Arabic text folding for search.

Arabic is written with several forms of the same letter, and people type
whichever is quickest. Someone looking for إسطنبول types "اسطنبول"; someone
looking for جدة types "جده"; someone looking for دبي types "دبى". A plain
`icontains` matches none of those, which on an Arabic-first site means the
picker looks broken to the people it was built for.

Folding both the stored text and the search term onto one canonical form is
what makes those searches land. It is deliberately lossy: the folded text is
only ever used for matching, never displayed.
"""

import re

# Harakat (fatha, damma, kasra, shadda, sukun, tanween) and the tatweel used to
# stretch a word. Neither changes the word; both break a literal match.
_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")

_FOLD = str.maketrans(
    {
        # Every hamza-bearing alef, and the bare one, fold together.
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        # Ta marbuta is routinely typed as ha.
        "ة": "ه",
        # Alef maqsura is routinely typed as ya, and vice versa.
        "ى": "ي",
        "ئ": "ي",
        "ؤ": "و",
        "ء": "",
        # Persian/Urdu keyboards produce these for Arabic letters.
        "ك": "ك",
        "ی": "ي",
        "ک": "ك",
        # Arabic-Indic digits, so "٥" and "5" match each other.
        "٠": "0",
        "١": "1",
        "٢": "2",
        "٣": "3",
        "٤": "4",
        "٥": "5",
        "٦": "6",
        "٧": "7",
        "٨": "8",
        "٩": "9",
    }
)


def normalize_arabic(text: str) -> str:
    """Fold `text` to the form used for matching. Safe on non-Arabic input."""
    if not text:
        return ""
    folded = _DIACRITICS.sub("", text).translate(_FOLD)
    # Collapse runs of whitespace so a stored blob joined from several fields
    # cannot fail a match on spacing alone.
    return " ".join(folded.lower().split())
