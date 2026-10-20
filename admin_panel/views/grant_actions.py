"""
grant_actions.py — حفظ بيانات المنحة القادمة من نماذج لوحة الإدارة.

كارد تفاصيل المنحة وكارد الأصناف وكارد المستفيدين مشتركة بين ثلاث صفحات
(الداشبورد، صفحة المانح، صفحة المستفيد)، فمعالجة طلباتها مجموعة هنا في مكان واحد:
    handle_grant_card_post()  ← نقطة الدخول من الصفحات الثلاث
"""
import json
import re
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect

from audit.recorder import field_changes, record_change
from audit.snapshots import counts_snapshot, grant_snapshot, items_snapshot
from entities.models import Beneficiary
from grants.models import Grant, GrantItem, GrantUpdate, Visit
from grants.page_data import items_payload
from grants.uploads import is_valid_upload
from grants.saving import parse_items_post, replace_beneficiary_counts, save_item_entry

from .page_data import counts_payload, items_limit


# ── قراءة قيم النماذج ────────────────────────────────────────────────────

def is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def load_json_field(post, key):
    """يقرأ حقل JSON من الطلب، ويرجع قائمة فارغة لو كان النص غير صالح."""
    try:
        return json.loads(post.get(key, "[]"))
    except ValueError:
        return []


def parse_amount(raw):
    """يحوّل نص المبلغ (مثال: "200,000") إلى Decimal، أو صفر لو كان فارغاً/غير صالح."""
    cleaned = re.sub(r"[^\d.]", "", raw)
    try:
        return Decimal(cleaned) if cleaned else Decimal("0")
    except InvalidOperation:
        return Decimal("0")


def parse_quantity_count(raw):
    """يحوّل نص عدد الأصناف بالقرار إلى رقم صحيح، أو None لو كان فارغاً/غير صالح."""
    raw = (raw or "").strip()
    try:
        return int(raw) if raw else None
    except ValueError:
        return None


def grant_type_from_label(label):
    return "in_kind" if label == "عيني" else "financial"


def grant_status_from_label(label):
    return "ongoing" if label == "جارية" else "ended"


# ── الزيارات والأخبار والإعلانات ─────────────────────────────────────────

def create_visits(grant, visits_data):
    """ينشئ زيارات المنحة — أي زيارة بدون تاريخ تُتجاهل."""
    for v in visits_data:
        visit_date = v.get("date")
        if visit_date:
            Visit.objects.create(grant=grant, visit_date=visit_date, description=(v.get("purpose") or "").strip())


def create_updates(grant, news_data, announcements_data):
    """ينشئ أخبار وإعلانات المنحة — العنوان والرابط إجباريان لكل منهما، والناقص يُتجاهل."""
    for n in news_data:
        title = (n.get("title") or "").strip()
        url = (n.get("url") or "").strip()
        if title and url:
            GrantUpdate.objects.create(grant=grant, type="news", title_ar=title, link=url)
    for a in announcements_data:
        text = (a.get("text") or "").strip() if isinstance(a, dict) else ""
        url = (a.get("url") or "").strip() if isinstance(a, dict) else ""
        if text and url:
            GrantUpdate.objects.create(grant=grant, type="announcement", title_ar=text, link=url)


# ── حفظ كروت المنحة ──────────────────────────────────────────────────────

def save_grant_from_post(request):
    """يحفظ تعديلات منحة موجودة من نموذج كارد التفاصيل."""
    post = request.POST
    grant = get_object_or_404(Grant, id=post.get("grant_id"))
    before = grant_snapshot(grant)

    grant.type = grant_type_from_label(post.get("type"))
    date_str = post.get("date")
    if date_str:
        grant.grant_date = date_str

    beneficiary_id = post.get("beneficiary_id")
    if beneficiary_id:
        beneficiary = Beneficiary.objects.filter(id=beneficiary_id).first()
        if beneficiary:
            grant.beneficiary = beneficiary

    grant.decision_number = (post.get("decisionNumber") or "").strip()
    grant.decision_date = post.get("decisionDate") or None
    grant.decision_quantity_count = parse_quantity_count(post.get("decisionQuantityCount"))
    grant.decision_quantity_type = (post.get("decisionQuantityType") or "").strip()
    grant.amount = parse_amount(post.get("amount", ""))
    grant.status = grant_status_from_label(post.get("status"))
    grant.save()

    # الزيارات — حذف وإعادة إنشاء
    visits_data = load_json_field(post, "visits_json")
    Visit.objects.filter(grant=grant).delete()
    create_visits(grant, visits_data)

    # الأخبار والإعلانات — حذف وإعادة إنشاء
    news_data = load_json_field(post, "news_json")
    announcements_data = load_json_field(post, "announcements_json")
    GrantUpdate.objects.filter(grant=grant).delete()
    create_updates(grant, news_data, announcements_data)

    changes = field_changes(before, grant_snapshot(grant))
    if changes:
        record_change(request.user, "updated", grant, "تعديل بيانات المنحة: " + "، ".join(changes), changes)
    return grant


def save_items_from_post(request):
    """يحفظ أصناف منحة عينية من كارد الأصناف المنفصل، مستقل تمامًا عن حفظ بقية بيانات المنحة.
    يرجّع (المنحة، حالة الحفظ) — الحالة فيها duplicateSerial و limitExceeded عشان الواجهة تعرض
    الخطأ داخل الكارد بدل رسالة نجاح مضللة. الحفظ كله ضمن معاملة واحدة: لو تكرر رقم تسلسلي
    ما يُحفظ أي شيء (ولا الحذف)، فيبقى ما كتبه المستخدم بالكارد كما هو ليصحّحه ويعيد الحفظ."""
    grant = get_object_or_404(Grant, id=request.POST.get("grant_id"))
    ajax = is_ajax(request)
    items_data, deleted_ids = parse_items_post(request.POST)

    flags = {"duplicateSerial": False, "limitExceeded": False, "invalidFile": False}

    # مرفق غير مسموح (نوع أو حجم) = لا يُحفظ أي شيء
    if not all(is_valid_upload(f, "attachment") for f in request.FILES.values()):
        flags["invalidFile"] = True
        if not ajax:
            messages.error(request, "invalid_file")
        return grant, flags

    limit = items_limit(grant)
    if limit is not None and len(items_data) > limit:
        items_data = items_data[:limit]
        flags["limitExceeded"] = True
        if not ajax:
            messages.error(request, "items_limit_exceeded")

    before = items_snapshot(grant)
    try:
        with transaction.atomic():
            if deleted_ids:
                GrantItem.objects.filter(grant=grant, id__in=deleted_ids).delete()
            for entry in items_data:
                save_item_entry(grant, entry, request.FILES)
        after = items_snapshot(grant)
        if after != before:
            record_change(request.user, "updated", grant, f"تعديل أصناف المنحة ({len(before)} ← {len(after)} صنف)", {"قبل": before, "بعد": after})
    except IntegrityError:
        flags["duplicateSerial"] = True
        if not ajax:
            messages.error(request, "duplicate_serial")

    return grant, flags


def save_counts_from_post(request):
    """يحفظ عدد ونوع المستفيدين لمنحة — نفس منطق واجهة المستفيد بالضبط، مستقل عن حفظ بقية بيانات المنحة."""
    grant = get_object_or_404(Grant, id=request.POST.get("grant_id"))
    before = counts_snapshot(grant)
    replace_beneficiary_counts(grant, request.POST)
    after = counts_snapshot(grant)
    if after != before:
        record_change(request.user, "updated", grant, "تعديل عدد ونوع المستفيدين", {"قبل": before, "بعد": after})
    return grant


def handle_grant_card_post(request, page_url):
    """يعالج طلبات الحفظ القادمة من كروت المنحة المشتركة (form_type = save_grant / save_items / save_counts).

    page_url: رابط الصفحة الحالية — يُعاد التوجيه له بعد الحفظ مع فتح نفس الكارد.
    يرجع الاستجابة المناسبة، أو None لو الطلب ليس من هذه الكروت (فتكمل الصفحة عملها العادي).
    """
    if request.method != "POST":
        return None
    form_type = request.POST.get("form_type")

    if form_type == "save_grant":
        grant = save_grant_from_post(request)
        return redirect(page_url + f"?open={grant.id}")

    if form_type == "save_items":
        grant, items_flags = save_items_from_post(request)
        if is_ajax(request):
            return JsonResponse({"items": items_payload(grant), "itemsLimit": items_limit(grant), **items_flags})
        return redirect(page_url + f"?open={grant.id}&items=1&saved=items")

    if form_type == "save_counts":
        grant = save_counts_from_post(request)
        if is_ajax(request):
            return JsonResponse({"beneficiaries": counts_payload(grant)})
        return redirect(page_url + f"?open={grant.id}&saved=counts")

    return None
