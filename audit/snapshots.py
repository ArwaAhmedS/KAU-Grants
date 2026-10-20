"""
snapshots.py — لقطة نصية مختصرة لبيانات سجل ما قبل التعديل وبعده، لتُحفظ الفروق في سجل التعديلات.
"""


def grant_snapshot(grant):
    return {
        "النوع": grant.get_type_display(),
        "تاريخ المنحة": str(grant.grant_date or ""),
        "الجهة المستفيدة": grant.beneficiary.name_ar if grant.beneficiary_id else "",
        "رقم القرار": grant.decision_number,
        "تاريخ القرار": str(grant.decision_date or ""),
        "العدد بالقرار": grant.decision_quantity_count,
        "نوع الصنف بالقرار": grant.decision_quantity_type,
        "المبلغ": "{:.2f}".format(grant.amount),
        "الحالة": grant.get_status_display(),
        "الزيارات": [f"{v.visit_date} {v.description}" for v in grant.visits.all().order_by("visit_date", "id")],
        "الأخبار": [f"{u.title_ar} {u.link}" for u in grant.updates.filter(type="news").order_by("id")],
        "الإعلانات": [f"{u.title_ar} {u.link}" for u in grant.updates.filter(type="announcement").order_by("id")],
    }


def counts_snapshot(grant):
    return [f"{c.display_category()}: {c.count}" for c in grant.counts.all().order_by("id")]


def items_snapshot(grant):
    return [
        f"{it.item_type} | {it.serial_number or '—'} | {it.get_condition_display()}"
        + (f" | مرفق: {it.attachment.name.rsplit('/', 1)[-1]}" if it.attachment else "")
        for it in grant.items.all().order_by("id")
    ]


def donor_snapshot(donor):
    return {
        "الاسم": donor.name_ar,
        "الشعار": donor.logo.name if donor.logo else "",
        "جهات التواصل": [f"{c.name} | {c.position} | {c.email} | {c.phone}" for c in donor.contacts.all().order_by("id")],
    }
