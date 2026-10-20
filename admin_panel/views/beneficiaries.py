"""
beneficiaries.py — صفحات الجهات المستفيدة بلوحة الإدارة: القائمة وصفحة الجهة الواحدة.
"""
from django.db.models import Max, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import manager_required
from audit.recorder import record_change
from entities.models import Beneficiary
from grants.models import BeneficiaryCount, Grant

from .grant_actions import handle_grant_card_post, is_ajax
from .page_data import grant_cards_context, grant_full_payload


@manager_required
def beneficiary_list(request):
    """صفحة إدارة الجهات المستفيدة (بحث + ترتيب + قائمة الجهات)."""
    beneficiaries_data = []
    for b in Beneficiary.objects.all().order_by("name_ar"):
        grants_qs = Grant.objects.filter(beneficiary=b)
        total_amount = grants_qs.aggregate(total=Sum("amount"))["total"] or 0
        total_beneficiaries = BeneficiaryCount.objects.filter(grant__beneficiary=b).aggregate(total=Sum("count"))["total"] or 0
        last_grant = grants_qs.aggregate(last=Max("grant_date"))["last"]
        beneficiaries_data.append({
            "id": b.id,
            "name": b.name_ar,
            "grantsCount": grants_qs.count(),
            "totalAmount": float(total_amount),
            "totalBeneficiaries": total_beneficiaries,
            "lastGrantDate": last_grant.isoformat() if last_grant else None,
        })
    return render(request, "admin_panel/beneficiary_list.html", {"beneficiaries_data": beneficiaries_data})


def save_beneficiary_from_post(request, beneficiary):
    """يحفظ تعديل اسم الجهة المستفيدة — يرد بـ JSON لطلبات AJAX وبإعادة توجيه لغيرها."""
    name = (request.POST.get("name") or "").strip()
    if name:
        old_name = beneficiary.name_ar
        beneficiary.name_ar = name
        beneficiary.save()
        if name != old_name:
            record_change(request.user, "updated", beneficiary, "تعديل اسم الجهة المستفيدة", {"الاسم": [old_name, name]})
        if is_ajax(request):
            return JsonResponse({"success": True, "name": beneficiary.name_ar})
        return redirect("beneficiary_detail", beneficiary_id=beneficiary.id)
    if is_ajax(request):
        return JsonResponse({"success": False, "error": "الاسم مطلوب"})
    return redirect("beneficiary_detail", beneficiary_id=beneficiary.id)


@manager_required
def beneficiary_detail(request, beneficiary_id):
    """صفحة تفاصيل جهة مستفيدة واحدة (بيانات الجهة + منحها)."""
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
    page_url = reverse("beneficiary_detail", kwargs={"beneficiary_id": beneficiary.id})

    if request.method == "POST" and request.POST.get("form_type") == "save_beneficiary":
        return save_beneficiary_from_post(request, beneficiary)

    response = handle_grant_card_post(request, page_url)
    if response:
        return response

    grants_qs = Grant.objects.filter(beneficiary=beneficiary).select_related("donor").order_by("-grant_date")
    total_beneficiaries = BeneficiaryCount.objects.filter(grant__beneficiary=beneficiary).aggregate(total=Sum("count"))["total"] or 0

    context = {
        "beneficiary_info": {"id": beneficiary.id, "name": beneficiary.name_ar},
        "grants_data": [grant_full_payload(g) for g in grants_qs],
        "total_beneficiaries": total_beneficiaries,
        **grant_cards_context(request),
    }
    return render(request, "admin_panel/beneficiary_detail.html", context)
