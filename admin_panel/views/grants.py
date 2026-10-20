"""
grants.py — إضافة منحة جديدة، ورفع/حذف تقرير الأثر الرسمي لمنحة.
"""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.decorators import manager_required
from audit.recorder import record_change
from audit.snapshots import counts_snapshot, grant_snapshot
from entities.models import Beneficiary, Donor
from grants.models import BeneficiaryCount, Grant, ImpactReport
from grants.uploads import is_valid_upload

from .grant_actions import (
    create_updates, create_visits, grant_status_from_label, grant_type_from_label,
    load_json_field, parse_amount, parse_quantity_count,
)


def create_initial_counts(grant, counts_data):
    """ينشئ أعداد المستفيدين التقديرية للمنحة الجديدة — الفئة المكررة أو ذات العدد صفر تُتجاهل."""
    seen_categories = set()
    for c in counts_data:
        category = c.get("category")
        if not category or category in seen_categories:
            continue
        seen_categories.add(category)
        try:
            count_value = int(c.get("count") or 0)
        except (TypeError, ValueError):
            count_value = 0
        if count_value > 0:
            other_label = (c.get("other_label") or "").strip()
            BeneficiaryCount.objects.create(
                grant=grant, category=category, count=count_value,
                other_label=other_label if category == "other" else "",
            )


@manager_required
def add_grant(request):
    """صفحة إضافة منحة جديدة (بيانات المنحة، المستفيدين، الزيارات، الأخبار، الإعلانات)."""
    if request.method == "POST":
        post = request.POST
        title = (post.get("title") or "").strip()
        donor_id = post.get("donor_id")
        donor_other = (post.get("donor_other") or "").strip()
        beneficiary_id = post.get("beneficiary_id")

        if not title or not beneficiary_id or not donor_id or (donor_id == "__other__" and not donor_other):
            messages.error(request, "بيانات المنحة الأساسية ناقصة")
            return redirect("add_grant")

        # "أخرى" = جهة مانحة جديدة تُنشأ باسمها مباشرة
        if donor_id == "__other__":
            donor = Donor.objects.create(name_ar=donor_other)
            record_change(request.user, "created", donor, "إضافة جهة مانحة (من نموذج إضافة منحة)")
        else:
            donor = get_object_or_404(Donor, id=donor_id)
        beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)

        amount = parse_amount(post.get("amount", ""))
        quantity_count = parse_quantity_count(post.get("decisionQuantityCount"))

        grant = Grant.objects.create(
            title_ar=title,
            donor=donor,
            beneficiary=beneficiary,
            type=grant_type_from_label(post.get("type")),
            amount=amount,
            grant_date=post.get("date") or timezone.now().date(),
            status=grant_status_from_label(post.get("status")),
            decision_number=(post.get("decisionNumber") or "").strip(),
            decision_date=post.get("decisionDate") or None,
            decision_quantity_count=quantity_count,
            decision_quantity_type=(post.get("decisionQuantityType") or "").strip(),
        )

        create_initial_counts(grant, load_json_field(post, "counts_json"))
        create_visits(grant, load_json_field(post, "visits_json"))
        create_updates(grant, load_json_field(post, "news_json"), load_json_field(post, "announcements_json"))
        record_change(request.user, "created", grant, "إضافة منحة",
                      {**grant_snapshot(grant), "المستفيدون": counts_snapshot(grant), "الجهة المانحة": donor.name_ar})

        return redirect(reverse("dashboard") + f"?open={grant.id}")

    context = {
        "donors_list": list(Donor.objects.all().order_by("name_ar").values("id", "name_ar")),
        "beneficiaries_list": list(Beneficiary.objects.all().order_by("name_ar").values("id", "name_ar")),
        "beneficiary_categories": BeneficiaryCount.CATEGORY_CHOICES,
    }
    return render(request, "admin_panel/add_grant.html", context)


@manager_required
def upload_grant_report(request, grant_id):
    """يرفع تقرير أثر رسمي لمنحة معيّنة ويحفظه في جدول ImpactReport،
    أو يحذفه (يُستخدم لمهلة التراجع بعد الرفع مباشرة — نفس مبدأ واجهة المستفيد)."""
    grant = get_object_or_404(Grant, id=grant_id)
    new_report_id = None
    rejected_file = False
    if request.method == "POST":
        if request.POST.get("action") == "delete":
            report = ImpactReport.objects.filter(
                id=request.POST.get("report_id"), grant=grant, stage="official"
            ).first()
            if report:
                record_change(request.user, "deleted", report, f"حذف تقرير أثر رسمي ({report.file.name.rsplit('/', 1)[-1]})",
                              {"المنحة": grant.title_ar})
                report.delete()
        elif request.FILES.get("file") and not is_valid_upload(request.FILES["file"], "report"):
            rejected_file = True
        elif request.FILES.get("file"):
            new_report = ImpactReport.objects.create(
                grant=grant,
                stage="official",
                report_date=timezone.now().date(),
                file=request.FILES["file"],
                uploaded_by=request.user if request.user.is_authenticated else None,
            )
            new_report_id = new_report.id
            record_change(request.user, "created", new_report, f"رفع تقرير أثر رسمي ({new_report.file.name.rsplit('/', 1)[-1]})",
                          {"المنحة": grant.title_ar})

    # نرجع للصفحة التي جاء منها الطلب مع إبقاء كارد التقرير مفتوحاً
    # (رابط الرجوع يُقبل فقط لو كان داخل هذا الموقع — حتى لا يُستغل لتحويل المستخدم لموقع خارجي)
    next_url = request.POST.get("next")
    if not next_url or not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = reverse("dashboard")
    sep = "&" if "?" in next_url else "?"
    url = f"{next_url}{sep}report={grant.id}"
    if new_report_id:
        url += f"&uploaded={new_report_id}"
    if rejected_file:
        url += "&upload_error=1"
    return redirect(url)
