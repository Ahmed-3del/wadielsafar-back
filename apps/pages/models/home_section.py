from django.db import models

from common.utilities import TimeStampedModel


class HomeSectionChoices(models.TextChoices):
    """The blocks the homepage is assembled from.

    The hero is deliberately absent: it carries the booking widget, which is
    the page's whole reason for existing, so it is always first and cannot be
    switched off. Everything below it is the editor's to arrange —
    RECOMMENDATIONS and LOYALTY included, both of which used to be hard-coded
    at a fixed point on the page and are now sections like any other.

    A key here needs a matching component on the site. The frontend skips a key
    it does not recognise, so adding one to this list without shipping the
    component leaves a gap rather than an error — but the two belong together.
    """

    # The "you might also like" rail under the search: whichever tab is open,
    # a short list from a different service. Reacts live to the tab even when
    # positioned away from the search box, because both read the same client
    # state — see src/components/search/search-tab-context.tsx on the frontend.
    RECOMMENDATIONS = "RECOMMENDATIONS", "You might also like (search cross-sell)"
    # The Orbit membership pitch. The programme itself lives off-site — this
    # is only the band that gets a visitor to notice it exists — so nothing
    # here depends on the reader's answer to the search above it.
    LOYALTY = "LOYALTY", "Loyalty programme banner"
    SERVICES = "SERVICES", "What we offer"
    SAVINGS = "SAVINGS", "Ways to save"
    EXPLORER = "EXPLORER", "Budget explorer"
    DESTINATIONS = "DESTINATIONS", "Popular destinations"
    PACKAGES = "PACKAGES", "Featured packages"
    OFFERS = "OFFERS", "Offers"
    VISAS = "VISAS", "Visa services"
    CRUISES = "CRUISES", "Cruises"
    TRUST = "TRUST", "Why travel with us"
    PARTNERS = "PARTNERS", "Partners"
    TESTIMONIALS = "TESTIMONIALS", "Testimonials"
    CTA = "CTA", "Closing call to action"


class HomeSection(TimeStampedModel):
    """One block on the homepage, and where it sits.

    Twelve sections shipped by default and the page ran to eighteen screens on
    a phone. Which of them earn their place is a commercial judgement that
    changes with the season and the inventory, so it belongs to whoever is
    running the site rather than to a deployment.
    """

    key = models.CharField(max_length=32, choices=HomeSectionChoices.choices, unique=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "key")

    def __str__(self):
        return f"{self.get_key_display()} ({self.order})"
