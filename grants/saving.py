"""
saving.py — حفظ بيانات المنحة القادمة من النماذج (الأصناف وأعداد المستفيدين).
يُستخدم من بوابة المستفيد (portal) ومن لوحة الإدارة (admin_panel) معاً،
عشان يبقى الحفظ بنفس الطريقة بالضبط في المكانين.
"""
import json

from django.shortcuts import get_object_or_404

from .models import BeneficiaryCount, GrantItem


# ── الأصناف (للمنح العينية) ──────────────────────────────────────────────

def parse_items_post(post):
    """يقرأ قائمة الأصناف وقائمة المعرّفات المحذوفة من الطلب. يرجع (items_data, deleted_ids)."""
    try:
        items_data = json.loads(post.get("items_json", "[]"))
        deleted_ids = json.loads(post.get("deleted_ids_json", "[]"))
    except ValueError:
        items_data, deleted_ids = [], []
    return items_data, deleted_ids


def save_item_entry(grant, entry, files):
    """يحفظ صنفاً واحداً (جديداً أو موجوداً) من بيانات الواجهة. قد يرمي IntegrityError لو تكرر الرقم التسلسلي."""
    item_id = entry.get("id")
    if item_id:
        item = get_object_or_404(GrantItem, id=item_id, grant=grant)
    else:
        item = GrantItem(grant=grant)
    item.item_type = entry.get("item_type", "")
    item.building = entry.get("building", "")
    item.floor = entry.get("floor", "")
    item.room = entry.get("room", "")
    item.model = entry.get("model", "")
    # رقم تسلسلي فارغ = بدون رقم (NULL)، حتى يُسمح بأكثر من صنف بلا رقم تسلسلي
    item.serial_number = (entry.get("serial_number") or "").strip() or None
    item.condition = entry.get("condition", "new")
    uploaded_file = files.get(f"file_{entry.get('uid')}")
    if uploaded_file:
        item.attachment = uploaded_file
    elif entry.get("clear_attachment"):
        item.attachment = None
    item.save()
    return item


# ── أعداد المستفيدين ─────────────────────────────────────────────────────

def replace_beneficiary_counts(grant, post):
    """يحذف كل فئات المستفيدين القديمة للمنحة ويعيد إنشاء اللي أُرسلت من النموذج فقط
    (يدعم إضافة/حذف فئات ديناميكياً من الواجهة)."""
    sent_categories = post.getlist("category")
    sent_values = post.getlist("count_value")
    sent_other_labels = post.getlist("other_label")
    BeneficiaryCount.objects.filter(grant=grant).delete()
    for i, category in enumerate(sent_categories):
        try:
            count = int(sent_values[i])
        except (ValueError, IndexError):
            count = 0
        other_label = (sent_other_labels[i].strip() if i < len(sent_other_labels) else "")
        if category:
            BeneficiaryCount.objects.create(
                grant=grant, category=category, count=count,
                other_label=other_label if category == "other" else "",
            )
