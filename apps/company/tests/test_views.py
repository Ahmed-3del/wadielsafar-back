import pytest
from rest_framework.test import APIClient

from apps.company.models import Branch, Certificate, SocialLink
from apps.company.tests.factories import (
    BranchFactory,
    CertificateFactory,
    SocialLinkFactory,
)
from apps.users.tests.factories import UserFactory
from common.constants import RoleChoices

pytestmark = pytest.mark.django_db


@pytest.fixture
def clean_company():
    """Branches and social links ship in a data migration, so they are already
    in the test database. Tests that count rows need to start from empty."""
    Branch.objects.all().delete()
    SocialLink.objects.all().delete()
    Certificate.objects.all().delete()


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


def test_a_branch_phone_has_to_look_like_a_phone_number(clean_company):
    response = as_editor().post(
        "/api/v1/company/branches/",
        {"name_ar": "فرع", "name_en": "Branch", "phone": "call us"},
    )

    assert response.status_code == 400
    assert "phone" in str(response.data).lower()


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
