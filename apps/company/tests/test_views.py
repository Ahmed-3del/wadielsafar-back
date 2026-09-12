import pytest
from rest_framework.test import APIClient

from apps.company.models import Branch, Certificate, PromoBar, Promotion, SocialLink
from apps.company.tests.factories import (
    BranchFactory,
    CertificateFactory,
    PromoBarFactory,
    PromotionFactory,
    SocialLinkFactory,
)
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


@pytest.fixture
def clean_company():
    """Branches, social links and the promo bar ship in a data migration, so
    they are already in the test database. Tests that count rows need to
    start from empty."""
    Branch.objects.all().delete()
    SocialLink.objects.all().delete()
    Certificate.objects.all().delete()
    Promotion.objects.all().delete()
    PromoBar.objects.all().delete()


def as_editor():
    client = APIClient()
    client.force_authenticate(user=UserFactory(role=RoleChoices.EDITOR))
    return client


# --------------------------------------------------------------- certificates


def test_public_sees_only_active_certificates(clean_company):
    CertificateFactory(is_active=True)
    CertificateFactory(is_active=False)

    assert APIClient().get("/api/v1/company/certificates/").data["count"] == 1


def test_content_manager_still_sees_a_certificate_they_switched_off(clean_company):
    CertificateFactory(is_active=False)

    assert as_editor().get("/api/v1/company/certificates/").data["count"] == 1


def test_public_cannot_add_a_certificate(clean_company):
    response = APIClient().post(
        "/api/v1/company/certificates/", {"name_ar": "شهادة", "name_en": "Certificate"}
    )

    assert response.status_code in (401, 403)
    assert Certificate.objects.count() == 0


def test_editor_can_add_a_certificate_with_a_badge_and_a_document(clean_company):
    response = as_editor().post(
        "/api/v1/company/certificates/",
        {
            "name_ar": "السجل التجاري",
            "name_en": "Commercial Registration",
            "issuer_ar": "وزارة التجارة",
            "issuer_en": "Ministry of Commerce",
            "image": "https://cdn.example.com/mc.png",
            "document": "https://cdn.example.com/cr.pdf",
        },
    )

    assert response.status_code == 201, response.data
    assert Certificate.objects.get().document.endswith(".pdf")


def test_a_certificate_needs_neither_a_badge_nor_a_document(clean_company):
    """One the company can name but has no artwork for is still worth listing —
    the footer renders it as a labelled credential instead of a badge."""
    response = as_editor().post(
        "/api/v1/company/certificates/",
        {"name_ar": "الرقم الضريبي", "name_en": "VAT", "reference_number": "3112759853"},
    )

    assert response.status_code == 201, response.data
    assert response.data["image"] is None
    assert response.data["document"] == ""


def test_certificates_come_back_in_the_order_editors_set(clean_company):
    CertificateFactory(name_en="Third", order=3)
    CertificateFactory(name_en="First", order=1)
    CertificateFactory(name_en="Second", order=2)

    names = [
        row["name_en"] for row in APIClient().get("/api/v1/company/certificates/").data["results"]
    ]

    assert names == ["First", "Second", "Third"]


# -------------------------------------------------------------------- branches


def test_public_sees_only_active_branches(clean_company):
    BranchFactory(is_active=True)
    BranchFactory(is_active=False)

    assert APIClient().get("/api/v1/company/branches/").data["count"] == 1


def test_editor_can_add_a_branch(clean_company):
    response = as_editor().post(
        "/api/v1/company/branches/",
        {
            "name_ar": "فرع جديد",
            "name_en": "New branch",
            "phone": "+966115602558",
            "phone_display": "+966 11 560 2558",
        },
    )

    assert response.status_code == 201, response.data
    assert Branch.objects.get().phone_display == "+966 11 560 2558"


def test_a_branch_can_carry_its_own_working_hours(clean_company):
    response = as_editor().post(
        "/api/v1/company/branches/",
        {
            "name_ar": "فرع جديد",
            "name_en": "New branch",
            "phone": "+966115602558",
            "working_hours_ar": "السبت – الخميس: ٩ ص – ٩ م",
            "working_hours_en": "Sat–Thu: 9am–9pm",
        },
    )

    assert response.status_code == 201, response.data
    assert response.data["working_hours_en"] == "Sat–Thu: 9am–9pm"


def test_a_branch_phone_has_to_look_like_a_phone_number(clean_company):
    response = as_editor().post(
        "/api/v1/company/branches/",
        {"name_ar": "فرع", "name_en": "Branch", "phone": "call us"},
    )

    assert response.status_code == 400
    assert "phone" in str(response.data).lower()


def test_a_branch_can_carry_its_own_google_maps_listing(clean_company):
    """Coordinates alone can only ever open a search; a pasted Maps link is
    what lets 'view on map' land on the branch's real listing — its own name,
    photo and reviews — instead of a pin labelled with a lat/lng string."""
    response = as_editor().post(
        "/api/v1/company/branches/",
        {
            "name_ar": "فرع",
            "name_en": "Branch",
            "phone": "+966115602558",
            "google_maps_url": "https://maps.app.goo.gl/example",
        },
    )

    assert response.status_code == 201, response.data
    assert response.data["google_maps_url"] == "https://maps.app.goo.gl/example"


def test_a_branch_can_carry_its_own_cover_photo(clean_company):
    response = as_editor().post(
        "/api/v1/company/branches/",
        {
            "name_ar": "فرع",
            "name_en": "Branch",
            "phone": "+966115602558",
            "cover_image": "https://cdn.example.com/branch.jpg",
        },
    )

    assert response.status_code == 201, response.data
    assert response.data["cover_image"] == "https://cdn.example.com/branch.jpg"


def test_the_shipped_branches_are_there():
    """They used to be hardcoded in the frontend; the migration moved them, and
    losing them would silently empty the footer."""
    response = APIClient().get("/api/v1/company/branches/")

    assert response.data["count"] >= 4
    assert response.data["results"][0]["phone"] == "+966115602558"


# --------------------------------------------------------------- social links


def test_public_sees_only_active_social_links(clean_company):
    SocialLinkFactory(platform="FACEBOOK", is_active=True)
    SocialLinkFactory(platform="X", is_active=False)

    assert APIClient().get("/api/v1/company/social-links/").data["count"] == 1


def test_editor_can_add_a_social_link(clean_company):
    response = as_editor().post(
        "/api/v1/company/social-links/",
        {"platform": "YOUTUBE", "url": "https://youtube.com/@wadialsafar"},
    )

    assert response.status_code == 201, response.data
    assert SocialLink.objects.get().platform == "YOUTUBE"


def test_a_network_the_site_has_no_mark_for_is_rejected(clean_company):
    """The platform drives which icon renders, so a free-text value would put a
    link in the footer with no recognisable badge."""
    response = as_editor().post(
        "/api/v1/company/social-links/",
        {"platform": "MYSPACE", "url": "https://myspace.com/wadialsafar"},
    )

    assert response.status_code == 400


def test_the_shipped_social_profiles_are_there():
    response = APIClient().get("/api/v1/company/social-links/")

    platforms = {row["platform"] for row in response.data["results"]}
    assert {"FACEBOOK", "INSTAGRAM", "X", "TIKTOK", "SNAPCHAT"} <= platforms


# ----------------------------------------------------------------- promotions


def test_public_sees_only_active_promotions(clean_company):
    PromotionFactory(is_active=True)
    PromotionFactory(is_active=False)

    assert APIClient().get("/api/v1/company/promotions/").data["count"] == 1


def test_public_cannot_change_a_discount(clean_company):
    """The percentages on the homepage are a commercial commitment, so writing
    one is an editor's job and nobody else's."""
    response = APIClient().post(
        "/api/v1/company/promotions/",
        {"title_ar": "عرض", "title_en": "Offer", "badge_en": "90%"},
    )

    assert response.status_code in (401, 403)
    assert Promotion.objects.count() == 0


def test_editor_can_publish_a_promotion_with_a_deadline(clean_company):
    """The homepage counts down to `ends_at` in public, so it has to survive
    the round trip exactly as it was set."""
    response = as_editor().post(
        "/api/v1/company/promotions/",
        {
            "title_ar": "عرض الحجز المبكر",
            "title_en": "Early bird",
            "icon": "CLOCK",
            "ends_at": "2027-01-31T20:59:00Z",
        },
    )

    assert response.status_code == 201, response.data
    promotion = Promotion.objects.get()
    assert promotion.ends_at.isoformat() == "2027-01-31T20:59:00+00:00"


def test_a_promotion_with_no_end_date_is_allowed(clean_company):
    """A standing offer has no deadline, and the card then shows no timer
    rather than counting down to an invented one."""
    response = as_editor().post(
        "/api/v1/company/promotions/",
        {"title_ar": "خصم العميل الجديد", "title_en": "New customer", "code": "WELCOME15"},
    )

    assert response.status_code == 201, response.data
    assert Promotion.objects.get().ends_at is None


def test_a_promotion_link_must_be_a_path_on_this_site(clean_company):
    """The website renders it through a localised Link, so an absolute URL
    would come out as /ar/https://example.com."""
    response = as_editor().post(
        "/api/v1/company/promotions/",
        {"title_ar": "عرض", "title_en": "Offer", "link": "https://example.com"},
    )

    assert response.status_code == 400


def test_a_promotion_can_point_its_claim_button_at_a_page(clean_company):
    response = as_editor().post(
        "/api/v1/company/promotions/",
        {
            "title_ar": "عرض الباقات",
            "title_en": "Package offer",
            "link": "/packages",
            "cta_label_en": "See the packages",
        },
    )

    assert response.status_code == 201, response.data
    assert response.data["link"] == "/packages"
    assert response.data["cta_label_en"] == "See the packages"


def test_a_blank_promotion_link_is_allowed(clean_company):
    """Blank means the contact form, carrying the offer and its code — the
    right answer for a discount an agent applies by hand."""
    response = as_editor().post(
        "/api/v1/company/promotions/",
        {"title_ar": "عرض", "title_en": "Offer", "code": "WELCOME15"},
    )

    assert response.status_code == 201, response.data
    assert response.data["link"] == ""


# ---------------------------------------------------------------- promo bar


def test_public_reads_the_active_promo_bar(clean_company):
    PromoBarFactory(headline_en="15% off", code="WELCOME15", is_active=True)

    response = APIClient().get("/api/v1/company/promo-bar/")

    assert response.status_code == 200
    assert response.data["headline_en"] == "15% off"
    assert response.data["code"] == "WELCOME15"


def test_public_gets_nothing_while_the_promo_bar_is_switched_off(clean_company):
    """Pausing an offer has to actually hide it — an editor preparing next
    month's wording is not ready for a visitor to see it yet."""
    PromoBarFactory(is_active=False)

    assert APIClient().get("/api/v1/company/promo-bar/").status_code == 404


def test_an_editor_still_sees_it_while_switched_off(clean_company):
    """Otherwise there would be no way to read it back in the panel in order
    to turn it on again."""
    PromoBarFactory(headline_en="Ramadan offer", is_active=False)

    response = as_editor().get("/api/v1/company/promo-bar/")

    assert response.status_code == 200
    assert response.data["headline_en"] == "Ramadan offer"
    assert response.data["is_active"] is False


def test_public_cannot_change_the_promo_bar(clean_company):
    PromoBarFactory(headline_en="Old wording")

    response = APIClient().patch(
        "/api/v1/company/promo-bar/", {"headline_en": "Hacked"}
    )

    assert response.status_code in (401, 403)
    assert PromoBar.objects.get().headline_en == "Old wording"


def test_an_editor_can_change_the_promo_bar(clean_company):
    PromoBarFactory(headline_en="Old wording", code="OLD10")

    response = as_editor().patch(
        "/api/v1/company/promo-bar/",
        {"headline_en": "New season, new savings", "code": "SEASON20"},
    )

    assert response.status_code == 200, response.data
    promo_bar = PromoBar.objects.get()
    assert promo_bar.headline_en == "New season, new savings"
    assert promo_bar.code == "SEASON20"


def test_there_is_always_exactly_one_promo_bar_to_edit(clean_company):
    """No create endpoint exists — editing always lands on the same row,
    whether the request arrives before or after one has been created."""
    as_editor().patch("/api/v1/company/promo-bar/", {"headline_en": "Changed"})
    second = as_editor().get("/api/v1/company/promo-bar/").data

    assert PromoBar.objects.count() == 1
    assert second["headline_en"] == "Changed"


def test_a_promo_bar_link_must_be_a_path_on_this_site(clean_company):
    PromoBarFactory()

    response = as_editor().patch(
        "/api/v1/company/promo-bar/", {"link": "https://example.com"}
    )

    assert response.status_code == 400


def test_a_blank_promo_bar_code_hides_the_chip(clean_company):
    """Not every offer needs a code to quote."""
    PromoBarFactory(code="WELCOME15")

    response = as_editor().patch("/api/v1/company/promo-bar/", {"code": ""})

    assert response.status_code == 200, response.data
    assert response.data["code"] == ""
