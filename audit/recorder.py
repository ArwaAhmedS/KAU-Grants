"""
recorder.py — تسجيل تعديل في سجل التعديلات. يُستدعى من الصفحات بعد نجاح الحفظ:

    record_change(request.user, "updated", grant, "تعديل بيانات المنحة", changes)
"""
from .models import ChangeLog


def record_change(user, action, obj, summary, changes=None, object_type=None):
    """action: created / updated / deleted — obj: السجل الذي تغيّر (منحة، جهة مانحة، ...)."""
    ChangeLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        username=getattr(user, "username", "") or "—",
        role=getattr(getattr(user, "role", None), "name", "") or "",
        action=action,
        object_type=object_type or obj._meta.verbose_name,
        object_id=str(obj.pk or ""),
        object_label=str(obj)[:255],
        summary=summary[:500],
        changes=changes or {},
    )


def field_changes(before, after):
    """يقارن لقطتين {اسم الحقل: قيمة} ويرجع ما تغيّر فقط: {اسم الحقل: [القديم، الجديد]}."""
    return {k: [before.get(k), after.get(k)] for k in after if before.get(k) != after.get(k)}
