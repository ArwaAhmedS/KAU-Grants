"""
file_access.py — فتح الملفات المرفوعة (كل ما يبدأ رابطه بـ /media/) بعد التحقق من صلاحية من يطلبه.

الملفات لا تُقدَّم كروابط مكشوفة: أي طلب لملف يمر على can_open() أولاً.

    الملف                         من يستطيع فتحه
    donor_logos/                  الجميع (الشعارات معروضة للعامة أصلاً)
    impact_reports/               الإداري — والمستفيد لتقارير منحه — والمانح للتقارير الرسمية من منحه فقط
    item_attachments/             الإداري — والمستفيد لمرفقات أصناف منحه
    أي ملف آخر (مثل exports/)     الإداري فقط

من ليس له صلاحية يرى "غير موجود" (404) حتى لا يُعرف أن الملف موجود أصلاً.
"""
import mimetypes
import os

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse, Http404
from django.utils._os import safe_join

from grants.models import GrantItem, ImpactReport

PUBLIC_FOLDERS = ("donor_logos/",)
# أنواع تُعرض داخل المتصفح (معاينة)، وكل ما عداها يُنزَّل كملف
INLINE_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".webp")


def _is_manager(user):
    return user.is_superuser or getattr(getattr(user, "role", None), "name", None) == "manager"


def can_open(user, path):
    """هل يستطيع هذا المستخدم فتح الملف المحفوظ بهذا المسار (نسبةً لمجلد media)؟"""
    if path.startswith(PUBLIC_FOLDERS):
        return True
    if not user.is_authenticated:
        return False
    if _is_manager(user):
        return True

    role = getattr(getattr(user, "role", None), "name", None)
    if path.startswith("impact_reports/"):
        reports = ImpactReport.objects.filter(file=path).select_related("grant")
        if role == "beneficiary" and user.beneficiary_id:
            return any(r.grant.beneficiary_id == user.beneficiary_id for r in reports)
        if role == "donor" and user.donor_id:
            return any(r.stage == "official" and r.grant.donor_id == user.donor_id for r in reports)
        return False
    if path.startswith("item_attachments/"):
        if role == "beneficiary" and user.beneficiary_id:
            return GrantItem.objects.filter(attachment=path, grant__beneficiary_id=user.beneficiary_id).exists()
        return False
    return False


def protected_media(request, path):
    try:
        full_path = safe_join(settings.MEDIA_ROOT, path)
    except SuspiciousFileOperation:
        raise Http404
    if not os.path.isfile(full_path):
        raise Http404

    if not can_open(request.user, path):
        if not request.user.is_authenticated:
            # رابط وصل لشخص غير مسجّل دخول: نوجّهه لتسجيل الدخول ثم نعيده للملف
            return redirect_to_login(request.get_full_path())
        raise Http404

    inline = full_path.lower().endswith(INLINE_EXTENSIONS)
    content_type = mimetypes.guess_type(full_path)[0] or "application/octet-stream"
    response = FileResponse(open(full_path, "rb"), as_attachment=not inline,
                            filename=os.path.basename(full_path), content_type=content_type)
    if not path.startswith(PUBLIC_FOLDERS):
        response["Cache-Control"] = "private, no-store"  # لا يُحفظ الملف الخاص في ذاكرة المتصفح أو الوسطاء
    return response
