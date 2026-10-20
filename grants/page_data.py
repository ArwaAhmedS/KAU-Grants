"""
page_data.py — تحويل بيانات المنحة إلى JSON للواجهة (مشترك بين بوابة المستفيد ولوحة الإدارة).
"""


def items_payload(grant):
    """قائمة أصناف المنحة (GrantItem) بصيغة JSON لعرضها/تحديثها بكارد الأصناف دون إعادة تحميل الصفحة."""
    return [
        {
            "uid": it.id, "id": it.id,
            "item_type": it.item_type, "condition": it.condition,
            "building": it.building, "floor": it.floor, "room": it.room,
            "model": it.model, "serial_number": it.serial_number or "",
            "attachment_name": (it.attachment.name.rsplit("/", 1)[-1] if it.attachment else ""),
            "attachment_url": (it.attachment.url if it.attachment else ""),
        }
        for it in grant.items.all()
    ]
