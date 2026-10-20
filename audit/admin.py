from django.contrib import admin

from .models import ChangeLog


@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    """للقراءة فقط: لا يمكن إضافة سجل أو تعديله أو حذفه من هنا."""
    list_display = ("created_at", "username", "role", "action", "object_type", "object_label", "summary")
    list_filter = ("action", "object_type", "role", "created_at")
    search_fields = ("username", "object_label", "summary")
    date_hierarchy = "created_at"
    readonly_fields = [f.name for f in ChangeLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
