"""
views — صفحات لوحة الإدارة (للمستخدم بدور manager فقط).

الملفات:
    dashboard.py      الصفحة الرئيسية: إحصاءات + بحث/فلترة المنح
    donors.py         الجهات المانحة: القائمة، الإضافة، صفحة الجهة
    beneficiaries.py  الجهات المستفيدة: القائمة، صفحة الجهة
    grants.py         إضافة منحة جديدة + رفع/حذف تقرير الأثر الرسمي
    grant_actions.py  حفظ تعديلات المنحة من الكروت المشتركة (بيانات، أصناف، مستفيدون)
    page_data.py      تحويل بيانات المنحة إلى JSON للواجهة
"""
from .beneficiaries import beneficiary_list, beneficiary_detail
from .dashboard import dashboard
from .donors import add_donor, donor_list, donor_detail
from .grants import add_grant, upload_grant_report

__all__ = [
    "dashboard",
    "add_donor", "donor_list", "donor_detail",
    "beneficiary_list", "beneficiary_detail",
    "add_grant", "upload_grant_report",
]
