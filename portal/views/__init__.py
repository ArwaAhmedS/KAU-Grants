"""
views — بوابتا الجهات المانحة والمستفيدة (كل حساب يرى بيانات جهته فقط).

الملفات:
    donor.py        بوابة المانح (عرض فقط): لوحة المنح + الجهات المستفيدة
    beneficiary.py  بوابة المستفيد: لوحة المنح (مع حفظ الأعداد/الأصناف/التقارير) + الجهات المانحة
    page_data.py    تحويل البيانات إلى JSON للواجهة
"""
from .beneficiary import beneficiary_dashboard, beneficiary_donors
from .donor import donor_beneficiaries, donor_dashboard

__all__ = ["donor_dashboard", "donor_beneficiaries", "beneficiary_dashboard", "beneficiary_donors"]
