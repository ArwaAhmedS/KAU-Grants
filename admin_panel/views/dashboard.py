"""
dashboard.py — الصفحة الرئيسية للوحة الإدارة.
"""
from django.shortcuts import render
from django.urls import reverse

from accounts.decorators import manager_required
from entities.models import Beneficiary, Donor
from grants.models import Grant

from .grant_actions import handle_grant_card_post
from .page_data import grant_cards_context, grant_full_payload


@manager_required
def dashboard(request):
    """لوحة التحكم: إحصاءات + بحث/فلترة عن المنح + تفاصيل منحة — بيانات حقيقية من قاعدة البيانات."""
    response = handle_grant_card_post(request, reverse("dashboard"))
    if response:
        return response

    grants_qs = Grant.objects.select_related("donor", "beneficiary").prefetch_related(
        "counts", "visits", "updates"
    ).order_by("-grant_date")

    context = {
        "initial_grants": [grant_full_payload(g) for g in grants_qs],
        "total_donors": Donor.objects.count(),
        "total_beneficiaries": Beneficiary.objects.count(),
        **grant_cards_context(request),
    }
    return render(request, "admin_panel/dashboard.html", context)
