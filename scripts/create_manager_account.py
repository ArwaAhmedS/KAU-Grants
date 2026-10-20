"""
create_manager_account.py — ينشئ (أو يحدّث) حساب الإداري.

كلمة المرور والإيميل يُقرآن من ملف .env (المتغيران MANAGER_PASSWORD و MANAGER_EMAIL) ولا يُكتبان هنا.

طريقة التشغيل (من مجلد المشروع):
    python manage.py shell < scripts/create_manager_account.py
"""
from decouple import config

from accounts.models import Role, User

password = config("MANAGER_PASSWORD", default="")
email = config("MANAGER_EMAIL", default="")
if not password:
    raise SystemExit("أضف MANAGER_PASSWORD إلى ملف .env ثم أعد التشغيل")

manager_role, _ = Role.objects.get_or_create(name=Role.ADMIN)

user, created = User.objects.get_or_create(
    username="arwa",
    defaults={"email": email, "role": manager_role},
)
user.role = manager_role
user.set_password(password)
user.save()

print("تم إنشاء حساب الإداري بنجاح:" if created else "تم تحديث حساب الإداري الموجود:")
print(" اسم المستخدم: arwa")
print(" كلمة المرور: كما في MANAGER_PASSWORD بملف .env")
