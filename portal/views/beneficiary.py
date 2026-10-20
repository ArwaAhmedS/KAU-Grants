"""
beneficiary.py — بوابة الجهة المستفيدة.

لوحة المستفيد تعرض منحه، وتستقبل أربعة نماذج (الحقل form_type يحدد أيها):
    counts         حفظ عدد ونوع المستفيدين
    save_items     حفظ أصناف المنحة العينية
    report         رفع تقرير أثر (أولي — يراجعه الإداري قبل اعتماده)
    delete_report  التراجع عن رفع تقرير أولي
"""
import re

from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.decorators import beneficiary_required
from audit.recorder import record_change
from audit.snapshots import counts_snapshot, items_snapshot
from entities.models import Donor
from grants.donor_categories import get_category_color, get_donor_category
from grants.models import BeneficiaryCount, Grant, GrantItem, ImpactReport
from grants.uploads import is_valid_upload
from grants.page_data import items_payload
from grants.saving import parse_items_post, replace_beneficiary_counts, save_item_entry

from .page_data import reports_payload


def _id_param(request, name):
    """يقرأ رقم معرّف من رابط الصفحة (?open=12). أي قيمة ليست أرقاماً فقط تُهمل —
    لأن هذه القيم تُكتب داخل كود Alpine بالصفحة، ونص غير موثوق هناك قد يُنفَّذ كـ JavaScript."""
    value = request.GET.get(name)
    return value if value and re.fullmatch(r"[0-9]+", value) else None


# ── معالجة النماذج ───────────────────────────────────────────────────────
# كل دالة ترجع الجزء الذي يُضاف لرابط إعادة التوجيه (لإعادة فتح الكارد المناسب)،
# أو ترجع استجابة جاهزة (JsonResponse) لطلبات AJAX.

def _save_counts(request, grant):
    before = counts_snapshot(grant)
    replace_beneficiary_counts(grant, request.POST)
    after = counts_snapshot(grant)
    if after != before:
        record_change(request.user, "updated", grant, "تعديل عدد ونوع المستفيدين", {"قبل": before, "بعد": after})
    return "&saved=counts"


def _save_items(request, grant):
    # نحدد إذا الطلب AJAX من البداية: الأخطاء بهالحالة تترجع ضمن الـ JSON نفسه
    # وتُعرض داخل الكرت مباشرة، فما نحتاج (ولا يصح) نضيفها لرسائل Django العامة
    # اللي تظهر ببانر أعلى الصفحة بمعزل عن سياق الكرت.
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    items_data, deleted_ids = parse_items_post(request.POST)
    limit_exceeded = False
    duplicate_serial = False

    # مرفق غير مسموح (نوع أو حجم) = لا يُحفظ أي شيء، ويبقى ما كتبه المستخدم بالكارد ليصحّحه
    if not all(is_valid_upload(f, "attachment") for f in request.FILES.values()):
        if is_ajax:
            return JsonResponse({
                "ok": False,
                "items": items_payload(grant),
                "limitExceeded": False,
                "duplicateSerial": False,
                "invalidFile": True,
                "itemsLimit": grant.decision_quantity_count,
            })
        messages.error(request, "invalid_file")
        return "&items=1"

    before = items_snapshot(grant)
    if deleted_ids:
        GrantItem.objects.filter(grant=grant, id__in=deleted_ids).delete()

    items_limit = grant.decision_quantity_count
    if items_limit is not None and len(items_data) > items_limit:
        items_data = items_data[:items_limit]
        limit_exceeded = True
        if not is_ajax:
            messages.error(request, "items_limit_exceeded")

    try:
        for entry in items_data:
            save_item_entry(grant, entry, request.FILES)
    except IntegrityError:
        duplicate_serial = True
        if not is_ajax:
            messages.error(request, "duplicate_serial")

    # (يُسجَّل ما حُفظ فعلاً، حتى لو توقف الحفظ عند رقم تسلسلي مكرر — الحفظ هنا صنفاً صنفاً)
    after = items_snapshot(grant)
    if after != before:
        record_change(request.user, "updated", grant, f"تعديل أصناف المنحة ({len(before)} ← {len(after)} صنف)", {"قبل": before, "بعد": after})

    if is_ajax:
        return JsonResponse({
            "ok": not duplicate_serial,
            "items": items_payload(grant),
            "limitExceeded": limit_exceeded,
            "duplicateSerial": duplicate_serial,
            "itemsLimit": items_limit,
        })
    return "&items=1&saved=items"


def _upload_report(request, grant):
    # ملاحظة: الواجهة تمنع الإرسال بدون ملف قبل ما توصل هنا (تحقق فوري داخل الكرت)،
    # فما نحتاج رسالة Django عامة هنا — لو وصل طلب بدون ملف (تجاوز للتحقق الأمامي) نتجاهله بصمت
    # بدل ما نعرض بانر خطأ بمعزل عن الكرت.
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return ""
    if not is_valid_upload(uploaded_file, "report"):
        messages.error(request, "invalid_file")
        return "&report=1"
    new_report = ImpactReport.objects.create(
        grant=grant, stage="preliminary",
        report_date=timezone.now().date(),
        file=uploaded_file, uploaded_by=request.user,
    )
    record_change(request.user, "created", new_report, f"رفع تقرير أثر أولي ({new_report.file.name.rsplit('/', 1)[-1]})", {"المنحة": grant.title_ar})
    return f"&uploaded={new_report.id}"


def _delete_report(request, grant):
    # المستفيد يحذف تقاريره الأولية فقط — التقارير الرسمية لا يملك حذفها
    report = get_object_or_404(ImpactReport, id=request.POST.get("report_id"), grant=grant, stage="preliminary")
    record_change(request.user, "deleted", report, f"حذف تقرير أثر أولي ({report.file.name.rsplit('/', 1)[-1]})", {"المنحة": grant.title_ar})
    report.delete()
    return "&report=1"


FORM_HANDLERS = {
    "counts": _save_counts,
    "save_items": _save_items,
    "report": _upload_report,
    "delete_report": _delete_report,
}


def _handle_post(request, beneficiary):
    # المنحة لازم تكون تابعة لنفس الجهة المستفيدة، وإلا 404 (عزل البيانات)
    grant = get_object_or_404(Grant, id=request.POST.get("grant_id"), beneficiary=beneficiary)
    handler = FORM_HANDLERS.get(request.POST.get("form_type"))
    result = handler(request, grant) if handler else ""
    if isinstance(result, JsonResponse):
        return result
    return redirect(reverse("beneficiary_dashboard") + f"?open={grant.id}" + result)


# ── الصفحات ──────────────────────────────────────────────────────────────

@beneficiary_required
def beneficiary_dashboard(request):
    """لوحة المستفيد: إحصاءاته ومنحه، مع كروت تعديل الأعداد والأصناف ورفع تقارير الأثر."""
    beneficiary = request.beneficiary

    if request.method == "POST":
        return _handle_post(request, beneficiary)

    grants_qs = Grant.objects.filter(beneficiary=beneficiary).select_related("donor").order_by("-grant_date")
    total_amount = grants_qs.aggregate(total=Sum("amount"))["total"] or 0
    total_beneficiaries = BeneficiaryCount.objects.filter(grant__beneficiary=beneficiary).aggregate(total=Sum("count"))["total"] or 0

    grants_data = []
    for grant in grants_qs:
        counts_json = [
            {"value": c.category, "label": c.display_category(), "count": c.count, "other_label": c.other_label}
            for c in grant.counts.all()
        ]
        reports = grant.reports.filter(stage="preliminary").order_by("-report_date", "-created_at")
        report_years = sorted({(r.report_date or r.created_at.date()).year for r in reports}, reverse=True)
        grants_data.append({
            "grant": grant,
            "items": grant.items.all(),
            "items_json": items_payload(grant),
            "items_script_id": f"items-data-{grant.id}",
            "items_limit": grant.decision_quantity_count,
            "damaged_count": sum(1 for it in grant.items.all() if it.condition == "damaged"),
            "counts_json": counts_json,
            "script_id": f"counts-data-{grant.id}",
            "reports": reports,
            "reports_json": reports_payload(reports),
            "reports_script_id": f"reports-data-{grant.id}",
            "report_years": report_years,
            "news": grant.updates.filter(type="news").order_by("-created_at"),
            "announcements": grant.updates.filter(type="announcement").order_by("-created_at"),
        })

    # أي كارد يُفتح تلقائياً بعد إعادة التوجيه (حسب باراميترات الرابط)
    open_grant_id = _id_param(request, "open")
    uploaded_report_id = _id_param(request, "uploaded")
    open_report_card = request.GET.get("report")
    show_report_card = bool(open_grant_id) and bool(uploaded_report_id or open_report_card)
    show_grant_card = bool(open_grant_id) and not show_report_card

    context = {
        "beneficiary": beneficiary,
        "grants_data": grants_data,
        "grants_count": grants_qs.count(),
        "total_beneficiaries": total_beneficiaries,
        "total_amount": total_amount,
        "all_categories_json": [{"value": v, "label": l} for v, l in BeneficiaryCount.CATEGORY_CHOICES],
        "open_grant_id": open_grant_id,
        "open_items": request.GET.get("items"),
        "uploaded_report_id": uploaded_report_id,
        "show_report_card": show_report_card,
        "show_grant_card": show_grant_card,
        "saved": request.GET.get("saved"),
    }
    return render(request, "portal/beneficiary_dashboard.html", context)


@beneficiary_required
def beneficiary_donors(request):
    """الجهات المانحة التي دعمت هذه الجهة المستفيدة، مع عدد منحها لها وفئة كل مانح."""
    beneficiary = request.beneficiary
    current_year = timezone.now().year
    donors = (
        Donor.objects.filter(grants__beneficiary=beneficiary).distinct()
        .annotate(ben_grants_count=Count("grants", filter=Q(grants__beneficiary=beneficiary), distinct=True))
    )
    donors_data = []
    for d in donors:
        # فئة المانح تُحسب من إجمالي كل منحه للسنة الحالية (لكل الجهات المستفيدة)،
        # عشان تطابق الفئة الظاهرة ببوابة المانح ولوحة الإدارة. عدد المنح يبقى خاصاً بهذه الجهة فقط.
        year_total = Grant.objects.filter(
            donor=d, grant_date__year=current_year
        ).aggregate(total=Sum("amount"))["total"] or 0
        category = get_donor_category(year_total)
        donors_data.append({
            "donor": d,
            "grants_count": d.ben_grants_count,
            "category": category,
            "category_color": get_category_color(category) if category else None,
        })
    return render(request, "portal/beneficiary_donors.html", {"beneficiary": beneficiary, "donors_data": donors_data})
