"""
login_protection.py — إيقاف تسجيل الدخول مؤقتاً بعد محاولات خاطئة متكررة.

بعد LOGIN_LOCKOUT_ATTEMPTS محاولات خاطئة (لنفس الحساب، أو من نفس الجهاز) خلال
LOGIN_LOCKOUT_MINUTES دقيقة، يُرفض الدخول حتى تنتهي المدة — حتى لو كانت كلمة المرور صحيحة،
فلا يمكن تجربة كلمات المرور واحدة تلو الأخرى. الإعدادان في config/settings.py.
"""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import LoginAttempt


def client_ip(request):
    return request.META.get("REMOTE_ADDR", "") or ""


def _normalise(username):
    return (username or "").strip().lower()


def is_locked_out(request, username):
    """True لو هذا الحساب أو هذا الجهاز تجاوز عدد المحاولات الخاطئة المسموح خلال المدة."""
    since = timezone.now() - timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
    recent = LoginAttempt.objects.filter(created_at__gte=since)
    limit = settings.LOGIN_LOCKOUT_ATTEMPTS
    return (
        recent.filter(username=_normalise(username)).count() >= limit
        or recent.filter(ip_address=client_ip(request)).count() >= limit
    )


def record_failed_login(request, username):
    LoginAttempt.objects.create(username=_normalise(username), ip_address=client_ip(request))
    # تنظيف: المحاولات الأقدم من يوم لا حاجة لها
    LoginAttempt.objects.filter(created_at__lt=timezone.now() - timedelta(days=1)).delete()


def clear_failed_logins(request, username):
    """بعد دخول ناجح: تُمسح المحاولات الخاطئة السابقة لهذا الحساب ومن هذا الجهاز."""
    LoginAttempt.objects.filter(username=_normalise(username)).delete()
    LoginAttempt.objects.filter(ip_address=client_ip(request)).delete()
