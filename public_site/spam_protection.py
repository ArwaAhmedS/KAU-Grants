"""
spam_protection.py — حماية نماذج الموقع العام من الإرسال الآلي والإغراق.

1) حقل مخفي (فخ): لا يراه الزائر ولا يملؤه، لكن برامج الإرسال الآلي تملأ كل الحقول.
   لو وصل ممتلئاً نرد بـ"تم الإرسال" دون إرسال شيء، حتى لا يعرف البرنامج أنه اكتُشف.
2) حد أقصى PUBLIC_FORM_LIMIT_PER_HOUR طلباً في الساعة لكل جهاز (الإعداد في config/settings.py).
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from accounts.login_protection import client_ip

from .models import PublicFormSubmission

HONEYPOT_FIELD = "contact_me_by_fax_only"


def is_bot(request):
    return bool(request.POST.get(HONEYPOT_FIELD))


def too_many_submissions(request):
    since = timezone.now() - timedelta(hours=1)
    count = PublicFormSubmission.objects.filter(ip_address=client_ip(request), created_at__gte=since).count()
    return count >= settings.PUBLIC_FORM_LIMIT_PER_HOUR


def record_submission(request, form):
    PublicFormSubmission.objects.create(ip_address=client_ip(request), form=form)
    PublicFormSubmission.objects.filter(created_at__lt=timezone.now() - timedelta(days=1)).delete()
