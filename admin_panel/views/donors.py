"""
donors.py — صفحات الجهات المانحة بلوحة الإدارة: القائمة، الإضافة، وصفحة الجهة الواحدة.
"""
from django.db.models import Max, Sum
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.decorators import manager_required
from audit.recorder import field_changes, record_change
from audit.snapshots import donor_snapshot
from entities.models import Donor, DonorContact
from grants.donor_categories import donor_category_history, get_donor_category
from grants.models import BeneficiaryCount, Grant
from grants.uploads import upload_error

from ..constants import CATEGORY_STYLES
from .grant_actions import handle_grant_card_post, load_json_field
from .page_data import grant_cards_context, grant_full_payload


def create_contacts(donor, contacts_data):
    """ينشئ جهات تواصل المانح من بيانات النموذج — الصف الفارغ تماماً يُتجاهل."""
    for c in contacts_data:
        name = (c.get("name") or "").strip()
        position = (c.get("title") or "").strip()
        email = (c.get("email") or "").strip()
        phone = (c.get("phone") or "").strip()
        if name or position or email or phone:
            DonorContact.objects.create(donor=donor, name=name, position=position, email=email, phone=phone)


@manager_required
def add_donor(request):
    """صفحة إضافة جهة مانحة جديدة — تُنشئ الجهة وجهات تواصلها في قاعدة البيانات."""
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        if not name:
            return redirect("add_donor")

        logo = request.FILES.get("logo")
        if logo and upload_error(logo, "logo"):
            return HttpResponseBadRequest(upload_error(logo, "logo"))

        donor = Donor.objects.create(name_ar=name, logo=logo)
        create_contacts(donor, load_json_field(request.POST, "contacts_json"))
        record_change(request.user, "created", donor, "إضافة جهة مانحة", donor_snapshot(donor))
        return redirect("donor_detail", donor_id=donor.id)

    return render(request, "admin_panel/add_donor.html")


@manager_required
def donor_list(request):
    """صفحة إدارة الجهات المانحة (بحث + فلاتر + قائمة الجهات)."""
    current_year = timezone.now().year

    donors_data = []
    for d in Donor.objects.all().order_by("name_ar"):
        grants_qs = Grant.objects.filter(donor=d)
        total_amount = grants_qs.aggregate(total=Sum("amount"))["total"] or 0
        year_total = grants_qs.filter(grant_date__year=current_year).aggregate(total=Sum("amount"))["total"] or 0
        last_grant = grants_qs.aggregate(last=Max("grant_date"))["last"]
        first_contact = d.contacts.first()
        donors_data.append({
            "id": d.id,
            "name": d.name_ar,
            "category": get_donor_category(year_total),
            "grants": grants_qs.count(),
            "logoUrl": d.logo.url if d.logo else None,
            "totalAmount": float(total_amount),
            "lastGrantDate": last_grant.isoformat() if last_grant else None,
            "email": first_contact.email if first_contact else None,
        })

    context = {
        "donors_data": donors_data,
        "category_styles": CATEGORY_STYLES,
    }
    return render(request, "admin_panel/donor_list.html", context)


def save_donor_from_post(request, donor):
    """يحفظ تعديل بيانات الجهة المانحة (الاسم، الشعار، جهات التواصل) من صفحة الجهة."""
    before = donor_snapshot(donor)
    name = (request.POST.get("name") or "").strip()
    if name:
        donor.name_ar = name
    if request.FILES.get("logo"):
        donor.logo = request.FILES["logo"]
    donor.save()

    # جهات التواصل — حذف وإعادة إنشاء
    contacts_data = load_json_field(request.POST, "contacts_json")
    DonorContact.objects.filter(donor=donor).delete()
    create_contacts(donor, contacts_data)

    changes = field_changes(before, donor_snapshot(donor))
    if changes:
        record_change(request.user, "updated", donor, "تعديل بيانات الجهة المانحة: " + "، ".join(changes), changes)


@manager_required
def donor_detail(request, donor_id):
    """صفحة تفاصيل جهة مانحة واحدة (بيانات الجهة + جهات التواصل + منحها)."""
    donor = get_object_or_404(Donor, id=donor_id)
    page_url = reverse("donor_detail", kwargs={"donor_id": donor.id})

    if request.method == "POST" and request.POST.get("form_type") == "save_donor":
        logo = request.FILES.get("logo")
        if logo and upload_error(logo, "logo"):
            return HttpResponseBadRequest(upload_error(logo, "logo"))
        save_donor_from_post(request, donor)
        return redirect("donor_detail", donor_id=donor.id)

    response = handle_grant_card_post(request, page_url)
    if response:
        return response

    current_year = timezone.now().year
    grants_qs = Grant.objects.filter(donor=donor).select_related("beneficiary").order_by("-grant_date")
    year_total = grants_qs.filter(grant_date__year=current_year).aggregate(total=Sum("amount"))["total"] or 0
    total_beneficiaries = BeneficiaryCount.objects.filter(grant__donor=donor).aggregate(total=Sum("count"))["total"] or 0

    context = {
        "donor_info": {
            "id": donor.id,
            "name": donor.name_ar,
            "logoUrl": donor.logo.url if donor.logo else None,
            "category": get_donor_category(year_total),
            "contacts": [
                {"name": c.name, "title": c.position, "email": c.email, "phone": c.phone}
                for c in donor.contacts.all()
            ],
        },
        "category_styles": CATEGORY_STYLES,
        "category_history": donor_category_history(grants_qs, current_year),
        "grants_data": [grant_full_payload(g) for g in grants_qs],
        "total_beneficiaries": total_beneficiaries,
        **grant_cards_context(request),
    }
    return render(request, "admin_panel/donor_detail.html", context)
