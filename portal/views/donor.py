"""
donor.py — بوابة الجهة المانحة (عرض فقط، بدون أي تعديل).
"""
from django.db.models import Count, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import donor_required
from entities.models import Beneficiary
from grants.donor_categories import donor_category_history, get_category_color, get_donor_category
from grants.models import BeneficiaryCount, Grant

from .page_data import reports_payload


@donor_required
def donor_dashboard(request):
    """لوحة المانح: هويته وفئته، إحصاءاته، ومنحه مع تفاصيلها وتقارير الأثر الرسمية فقط."""
    donor = request.donor
    current_year = timezone.now().year
    grants_qs = Grant.objects.filter(donor=donor).select_related("beneficiary").order_by("-grant_date")
    year_total = grants_qs.filter(grant_date__year=current_year).aggregate(total=Sum("amount"))["total"] or 0
    total_amount = grants_qs.aggregate(total=Sum("amount"))["total"] or 0
    total_beneficiaries = BeneficiaryCount.objects.filter(grant__donor=donor).aggregate(total=Sum("count"))["total"] or 0

    category_history = [
        {**entry, "color": get_category_color(entry["category"])}
        for entry in donor_category_history(grants_qs, current_year)
    ]

    grants_data = []
    for grant in grants_qs:
        reports_qs = grant.reports.filter(stage="official").order_by("-report_date")
        grants_data.append({
            "grant": grant,
            "counts": grant.counts.filter(count__gt=0),
            "visits": grant.visits.all().order_by("visit_date"),
            "news": grant.updates.filter(type="news").order_by("-created_at"),
            "announcements": grant.updates.filter(type="announcement").order_by("-created_at"),
            "reports": reports_qs,
            "reports_json": reports_payload(reports_qs),
            "reports_script_id": f"reports-data-{grant.id}",
        })

    context = {
        "donor": donor,
        "grants_data": grants_data,
        "grants_count": grants_qs.count(),
        "total_beneficiaries": total_beneficiaries,
        "total_amount": total_amount,
        "category": get_donor_category(year_total),
        "current_year": current_year,
        "donor_contacts": donor.contacts.all(),
        "category_history": category_history,
    }
    return render(request, "portal/donor_dashboard.html", context)


@donor_required
def donor_beneficiaries(request):
    """الجهات المستفيدة من منح هذا المانح، مع عدد المنح وإجمالي المستفيدين لكل جهة."""
    donor = request.donor
    beneficiaries = (
        Beneficiary.objects.filter(grants__donor=donor).distinct()
        .annotate(donor_grants_count=Count("grants", filter=Q(grants__donor=donor), distinct=True))
    )
    beneficiaries_data = []
    for b in beneficiaries:
        total = BeneficiaryCount.objects.filter(grant__donor=donor, grant__beneficiary=b).aggregate(total=Sum("count"))["total"] or 0
        beneficiaries_data.append({"beneficiary": b, "grants_count": b.donor_grants_count, "total_beneficiaries": total})
    return render(request, "portal/donor_beneficiaries.html", {"donor": donor, "beneficiaries_data": beneficiaries_data})
