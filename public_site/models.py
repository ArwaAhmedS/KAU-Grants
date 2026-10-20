"""
models.py — سجل إرسال نماذج الموقع العام (يُستخدم فقط لتحديد عدد الطلبات المسموح لكل زائر).
"""
from django.db import models


class PublicFormSubmission(models.Model):
    ip_address = models.CharField("عنوان الجهاز", max_length=45, db_index=True)
    form = models.CharField("النموذج", max_length=30)
    created_at = models.DateTimeField("الوقت", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "إرسال نموذج"
        verbose_name_plural = "إرسال نماذج الموقع العام"
