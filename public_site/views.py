"""
views.py — صفحات الموقع العام: "الرئيسية" + "قبول المنح" + "اتصل بنا"، واستقبال نماذجها.

المحتوى الثابت (الأخبار، الشركاء، الأهداف...) في content.py،
وإرسال الإيميل وحفظ ملف Excel في form_delivery.py.
"""
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from . import content
from .form_delivery import append_grant_to_excel, send_request_email
from .spam_protection import is_bot, record_submission, too_many_submissions


def _guard_public_form(request, form_name):
    """فحوص مشتركة لنماذج الموقع العام. يرجع ردّاً جاهزاً لو يجب إيقاف الطلب، أو None للمتابعة."""
    if is_bot(request):
        # برنامج آلي ملأ الحقل المخفي: نرد بنجاح شكلي دون إرسال أي شيء
        return JsonResponse({"success": True})
    if too_many_submissions(request):
        return JsonResponse({"success": False, "error": "too_many"}, status=429)
    record_submission(request, form_name)
    return None


# ── الصفحات ──────────────────────────────────────────────────────────────

def home(request):
    context = {
        "program_steps": content.PROGRAM_STEPS,
        "goals": content.GOALS,
        # تُكرَّر القائمة مرتين ليستمر شريط الأخبار المتحرك بلا فجوة
        "news_items_loop": (content.NEWS_ITEMS * 2),
        "resource_cards": content.RESOURCE_CARDS,
        "partners": content.PARTNERS,
        "partners_cols": 10,
        "partners_gap_total": 90,
        "contact_items": content.CONTACT_ITEMS,
    }
    return render(request, "public_site/home.html", context)


def grant_acceptance(request):
    context = {
        "program_steps": content.PROGRAM_STEPS,
        "contact_items": content.GRANT_CONTACT_ITEMS,
    }
    return render(request, "public_site/grant_acceptance.html", context)


def suggestions(request):
    context = {
        "contact_items": content.SUGGESTIONS_CONTACT_ITEMS,
    }
    return render(request, "public_site/suggestions.html", context)


# ── استقبال النماذج (تُرسل من الصفحات عبر fetch وترد بـ JSON) ────────────

def submit_grant(request):
    """نموذج "تقديم منحة": يُرسل بالإيميل للإدارة ويُضاف لملف Excel."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "invalid_method"}, status=405)
    stop = _guard_public_form(request, "grant")
    if stop:
        return stop

    donor_name = request.POST.get("donor_name", "")
    phone = request.POST.get("phone", "")
    donation_type = request.POST.get("donation_type", "")
    email = request.POST.get("email", "")
    notes = request.POST.get("notes", "")

    rows = [
        {"label": "الاسم / الجهة المتبرعة", "value": donor_name},
        {"label": "رقم التواصل", "value": phone},
        {"label": "نوع التبرع", "value": donation_type},
        {"label": "البريد الإلكتروني", "value": email},
        {"label": "ملاحظات", "value": notes},
    ]

    try:
        send_request_email("طلب تقديم منحة جديد", rows)
        append_grant_to_excel({
            "التاريخ": timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M"),
            "الاسم / الجهة": donor_name,
            "رقم التواصل": phone,
            "نوع التبرع": donation_type,
            "البريد الإلكتروني": email,
            "ملاحظات": notes,
        })
        return JsonResponse({"success": True})
    except Exception:
        return JsonResponse({"success": False, "error": "send_failed"}, status=500)


def submit_suggestion(request):
    """نماذج الاقتراحات الثلاثة (خارج الجامعة / داخل الجامعة / منسوبين وطلبة): تُرسل بالإيميل فقط."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "invalid_method"}, status=405)

    form = content.SUGGESTION_FORMS.get(request.POST.get("form_type", ""))
    if form is None:
        return JsonResponse({"success": False, "error": "invalid_form_type"}, status=400)
    stop = _guard_public_form(request, "suggestion_" + request.POST.get("form_type", ""))
    if stop:
        return stop

    rows = [{"label": label, "value": request.POST.get(field, "")} for label, field in form["fields"]]

    try:
        send_request_email(form["subject"], rows)
        return JsonResponse({"success": True})
    except Exception:
        return JsonResponse({"success": False, "error": "send_failed"}, status=500)
