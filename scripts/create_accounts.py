"""
create_accounts.py — ينشئ الأدوار الثلاثة وحساباً تجريبياً لكل دور (أدمن، مانح، مستفيد).

كلمة المرور (نفسها للحسابات الثلاثة) تُقرأ من ملف .env (المتغير SAMPLE_ACCOUNTS_PASSWORD) ولا تُكتب هنا.
هذه حسابات تجريبية للتطوير فقط — لا تشغّل هذا الملف على قاعدة بيانات حقيقية.

طريقة التشغيل (من مجلد المشروع):
    python manage.py shell < scripts/create_accounts.py
"""
from decouple import config

from accounts.models import Role, User
from entities.models import Donor, Beneficiary

password = config("SAMPLE_ACCOUNTS_PASSWORD", default="")
if not password:
    raise SystemExit("أضف SAMPLE_ACCOUNTS_PASSWORD إلى ملف .env ثم أعد التشغيل")

# 1) الأدوار الثلاثة (لو موجودة من قبل، ما بيصير خطأ)
manager_role, _ = Role.objects.get_or_create(name=Role.ADMIN)
donor_role, _ = Role.objects.get_or_create(name=Role.DONOR)
beneficiary_role, _ = Role.objects.get_or_create(name=Role.BENEFICIARY)

# 2) حساب الأدمن (وصول كامل لـ /admin/)
admin_user, created = User.objects.get_or_create(
    username="admin",
    defaults={
        "email": "admin@example.com",
        "role": manager_role,
        "is_staff": True,
        "is_superuser": True,
    },
)
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.role = manager_role
admin_user.set_password(password)
admin_user.save()

# 3) حساب مانح تجريبي (مرتبط بجهة مانحة تجريبية)
donor_entity, _ = Donor.objects.get_or_create(name_ar="جهة مانحة تجريبية")
donor_user, created = User.objects.get_or_create(
    username="donor1",
    defaults={"email": "donor1@example.com", "role": donor_role, "donor": donor_entity},
)
donor_user.role = donor_role
donor_user.donor = donor_entity
donor_user.set_password(password)
donor_user.save()

# 4) حساب مستفيد تجريبي (مرتبط بجهة مستفيدة تجريبية)
beneficiary_entity, _ = Beneficiary.objects.get_or_create(name_ar="جهة مستفيدة تجريبية", type="college")
beneficiary_user, created = User.objects.get_or_create(
    username="beneficiary1",
    defaults={"email": "beneficiary1@example.com", "role": beneficiary_role, "beneficiary": beneficiary_entity},
)
beneficiary_user.role = beneficiary_role
beneficiary_user.beneficiary = beneficiary_entity
beneficiary_user.set_password(password)
beneficiary_user.save()

print("تم إنشاء الحسابات الثلاثة بنجاح:")
print(" admin / donor1 / beneficiary1 — كلمة المرور كما في SAMPLE_ACCOUNTS_PASSWORD بملف .env")
