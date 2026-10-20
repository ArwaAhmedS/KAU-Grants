"""
views.py — تسجيل الدخول والخروج للأدوار الثلاثة (مانح، مستفيد، إداري).
"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .login_protection import clear_failed_logins, is_locked_out, record_failed_login


def _redirect_after_login(role):
    """الصفحة التي يُوجَّه لها المستخدم بعد الدخول، حسب دوره."""
    if role == "manager":
        return redirect("dashboard")
    elif role == "donor":
        return redirect("donor_dashboard")
    else:
        return redirect("beneficiary_dashboard")


def _try_login(request, role):
    """يتحقق من بيانات الدخول ومن مطابقة دور الحساب للبوابة المختارة.
    يرجع إعادة توجيه عند النجاح، أو None مع رسالة خطأ (locked_out / wrong_role / invalid_credentials) عند الفشل."""
    username = request.POST.get("username")
    password = request.POST.get("password")

    # بعد محاولات خاطئة متكررة: لا نتحقق من كلمة المرور أصلاً حتى تنتهي مدة الإيقاف
    if is_locked_out(request, username):
        messages.error(request, "locked_out")
        return None

    user = authenticate(request, username=username, password=password)

    if user is None:
        record_failed_login(request, username)
        messages.error(request, "invalid_credentials")
        return None
    if user.role.name != role:
        messages.error(request, "wrong_role")
        return None

    clear_failed_logins(request, username)
    login(request, user)
    return _redirect_after_login(role)


@login_required
@require_POST  # الخروج بزر فقط (POST مع رمز CSRF) — حتى لا يستطيع موقع آخر تسجيل خروج المستخدم برابط
def logout_view(request):
    logout(request)
    return redirect("role_login")


def role_login_view(request, role=None):
    # صفحة دخول مخصّصة لدور معيّن (وصلنا لها من رابط مباشر مثل /accounts/portal-login/donor/)
    if role:
        if request.method == "POST":
            response = _try_login(request, request.POST.get("role", role))
            if response:
                return response
        return render(request, "accounts/role_login_page.html", {"active_role": role})

    # صفحة اختيار نوع الحساب (الكروت الثلاثة)
    if request.method == "POST":
        role = request.POST.get("role", "")
        response = _try_login(request, role)
        if response:
            return response
        # لو صار خطأ، نرجّع نفس الصفحة مع تفعيل نفس الكرت اللي اختاره
        return render(request, "accounts/portal_select.html", {"active_role": role})

    return render(request, "accounts/portal_select.html", {"active_role": ""})
