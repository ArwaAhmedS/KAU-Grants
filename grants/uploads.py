"""
uploads.py — قواعد الملفات المرفوعة في النظام: الأنواع المسموحة والحجم الأقصى لكل نوع رفع.

    report      تقرير الأثر (من المستفيد أو الإداري)
    attachment  مرفق صنف من أصناف المنحة العينية
    logo        شعار الجهة المانحة

الفحص يتأكد من ثلاثة أشياء: امتداد الملف، وحجمه، وأن محتواه فعلاً من نفس النوع
(أول بايتات الملف) — حتى لا يُرفع ملف ضار بعد إعادة تسميته بامتداد مسموح.
"""
import os

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

MB = 1024 * 1024

UPLOAD_RULES = {
    "report": {"extensions": (".pdf", ".doc", ".docx"), "max_size": 10 * MB},
    "attachment": {"extensions": (".pdf", ".jpg", ".jpeg", ".png", ".webp", ".doc", ".docx", ".xls", ".xlsx"), "max_size": 10 * MB},
    "logo": {"extensions": (".png", ".jpg", ".jpeg", ".webp"), "max_size": 2 * MB},
}

# أول بايتات كل نوع ملف (ما يُعرف بالتوقيع)
_OFFICE_ZIP = b"PK\x03\x04"                          # docx / xlsx
_OFFICE_OLD = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"     # doc / xls
SIGNATURES = {
    ".pdf": (b"%PDF",),
    ".docx": (_OFFICE_ZIP,), ".xlsx": (_OFFICE_ZIP,),
    ".doc": (_OFFICE_OLD,), ".xls": (_OFFICE_OLD,),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",), ".jpeg": (b"\xff\xd8\xff",),
    ".webp": (b"RIFF",),
}


def upload_error(uploaded_file, kind):
    """يرجع رسالة الخطأ (بالعربي) لو الملف غير مقبول لهذا النوع من الرفع، أو None لو كان سليماً."""
    rules = UPLOAD_RULES[kind]
    extension = os.path.splitext(uploaded_file.name or "")[1].lower()
    allowed = "، ".join(e.lstrip(".").upper() for e in rules["extensions"])

    if extension not in rules["extensions"]:
        return f"نوع الملف غير مسموح. الأنواع المسموحة: {allowed}"
    if uploaded_file.size > rules["max_size"]:
        return f"حجم الملف أكبر من المسموح ({rules['max_size'] // MB} ميغابايت)"

    position = uploaded_file.tell() if hasattr(uploaded_file, "tell") else 0
    uploaded_file.seek(0)
    head = uploaded_file.read(16)
    uploaded_file.seek(position)
    if not any(head.startswith(sig) for sig in SIGNATURES[extension]):
        return "محتوى الملف لا يطابق امتداده"
    if extension == ".webp" and head[8:12] != b"WEBP":
        return "محتوى الملف لا يطابق امتداده"
    return None


def is_valid_upload(uploaded_file, kind):
    return upload_error(uploaded_file, kind) is None


@deconstructible
class UploadValidator:
    """نفس الفحص كـ validator لحقول الموديل — يطبَّق تلقائياً في لوحة Django Admin (/admin/)."""

    def __init__(self, kind):
        self.kind = kind

    def __call__(self, value):
        error = upload_error(value, self.kind)
        if error:
            raise ValidationError(error)

    def __eq__(self, other):
        return isinstance(other, UploadValidator) and other.kind == self.kind
