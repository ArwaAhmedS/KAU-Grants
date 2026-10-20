"""
page_data.py — تحويل بيانات المنحة إلى قواميس JSON تُعرض بكروت لوحة الإدارة
(نفس الشكل بالضبط بالداشبورد وصفحتي المانح والمستفيد).
"""
import re

from entities.models import Beneficiary
from grants.models import BeneficiaryCount
from grants.page_data import items_payload


def reports_payload(grant):
    """قائمة تقارير الأثر لمنحة معيّنة (من جدول ImpactReport) لعرضها بكارد التقرير."""
    out = []
    for r in grant.reports.all().order_by("created_at"):
        d = r.report_date or r.created_at.date()
        file_name = r.file.name.rsplit("/", 1)[-1] if r.file else ""
        out.append({
            "id": r.id,
            "label": f"تقرير {d.day}/{d.month}/{d.year}",
            "fileName": file_name,
            "url": r.file.url if r.file else "",
            "stage": r.stage,
            "stageLabel": r.get_stage_display(),
            "isPdf": file_name.lower().endswith(".pdf"),
        })
    return out


def counts_payload(grant):
    """قائمة عدد ونوع المستفيدين لمنحة (BeneficiaryCount) — يدعم فئة "أخرى" باسم مخصص."""
    return [
        {"category": c.category, "categoryLabel": c.display_category(), "count": c.count, "other_label": c.other_label}
        for c in grant.counts.all()
    ]


def items_limit(grant):
    """الحد الأقصى لعدد أصناف المنحة العينية = العدد المذكور بقرار قبول المنحة (أو None لو غير محدد)."""
    return grant.decision_quantity_count


def grant_full_payload(g):
    """القاموس الكامل لمنحة معيّنة (كل الحقول + المستفيدين + الزيارات + الأخبار + الإعلانات + التقارير + الأصناف)
    لعرضها بكارد تفاصيل المنحة القابل للتعديل."""
    return {
        "id": g.id,
        "title": g.title_ar,
        "type": g.get_type_display(),
        "donor": g.donor.name_ar,
        "donorId": g.donor_id,
        "beneficiary": g.beneficiary.name_ar,
        "beneficiaryId": g.beneficiary_id,
        "decisionNumber": g.decision_number,
        "decisionDate": g.decision_date.isoformat() if g.decision_date else "",
        "decisionQuantityCount": g.decision_quantity_count,
        "decisionQuantityType": g.decision_quantity_type,
        "date": g.grant_date.isoformat() if g.grant_date else "",
        "amount": "{:,.0f}".format(g.amount),
        "status": g.get_status_display(),
        "beneficiaries": counts_payload(g),
        "visits": [
            {"date": v.visit_date.isoformat() if v.visit_date else "", "purpose": v.description}
            for v in g.visits.all().order_by("visit_date")
        ],
        "news": [
            {"title": u.title_ar, "url": u.link}
            for u in g.updates.all() if u.type == "news"
        ],
        "announcements": [
            {"text": u.title_ar, "url": u.link}
            for u in g.updates.all() if u.type == "announcement"
        ],
        "reports": reports_payload(g),
        "items": items_payload(g),
        "itemsLimit": items_limit(g),
    }


def _id_param(request, name):
    """رقم معرّف من رابط الصفحة (?open=12) — أي قيمة ليست أرقاماً فقط تُهمل."""
    value = request.GET.get(name)
    return value if value and re.fullmatch(r"[0-9]+", value) else None


def grant_cards_context(request):
    """عناصر السياق المشتركة التي تحتاجها كروت المنحة (تفاصيل/أصناف/تقرير) بأي صفحة تعرضها."""
    return {
        "beneficiaries_list": list(Beneficiary.objects.all().order_by("name_ar").values("id", "name_ar")),
        "beneficiary_categories": BeneficiaryCount.CATEGORY_CHOICES,
        "open_grant_id": _id_param(request, "open"),
        "open_report_grant_id": _id_param(request, "report"),
        "open_items": request.GET.get("items"),
    }
