"""
models.py — سجل التعديلات: من غيّر ماذا ومتى (يُعرض للقراءة فقط في Django Admin).
"""
from django.conf import settings
from django.db import models


class ChangeLog(models.Model):
    ACTION_CHOICES = [
        ("created", "إضافة"),
        ("updated", "تعديل"),
        ("deleted", "حذف"),
    ]
    created_at = models.DateTimeField("الوقت", auto_now_add=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")
    # نحفظ اسم المستخدم ودوره كنص أيضاً، حتى يبقى السجل مفهوماً لو حُذف الحساب لاحقاً
    username = models.CharField("اسم المستخدم", max_length=150)
    role = models.CharField("الدور", max_length=20, blank=True)
    action = models.CharField("العملية", max_length=20, choices=ACTION_CHOICES)
    object_type = models.CharField("نوع السجل", max_length=50)
    object_id = models.CharField("رقم السجل", max_length=50, blank=True)
    object_label = models.CharField("السجل", max_length=255, blank=True)
    summary = models.CharField("ملخص", max_length=500)
    changes = models.JSONField("التفاصيل", default=dict, blank=True)

    def __str__(self):
        return f"{self.username}: {self.summary}"

    class Meta:
        verbose_name = "تعديل"
        verbose_name_plural = "سجل التعديلات"
        ordering = ["-created_at", "-id"]
