"""
page_data.py — تحويل بيانات البوابة إلى JSON للواجهة.
"""


def reports_payload(reports_qs):
    """قائمة تقارير الأثر بصيغة JSON (لعرضها بكارد التقرير)، مع تحديد ما إذا كان الملف PDF
    (قابل للمعاينة داخل الصفحة) أو لا (Word مثلاً)، لعرض بديل مناسب بدل معاينة فارغة."""
    out = []
    for r in reports_qs:
        d = r.report_date or r.created_at.date()
        file_name = r.file.name.rsplit("/", 1)[-1] if r.file else ""
        out.append({
            "id": r.id,
            "label": f"تقرير {d.day}/{d.month}/{d.year}",
            "fileName": file_name,
            "url": r.file.url if r.file else "",
            "isPdf": file_name.lower().endswith(".pdf"),
        })
    return out
