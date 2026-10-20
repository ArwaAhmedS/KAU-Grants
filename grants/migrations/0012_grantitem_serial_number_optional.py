# Generated manually: يجعل الرقم التسلسلي للصنف اختيارياً (NULL عند عدم إدخاله) بدل نص فارغ،
# عشان يُسمح بأكثر من صنف بلا رقم تسلسلي — شرط التفرّد يبقى مطبّقاً على الأرقام المُدخلة فعلاً.
# يحوّل أي رقم تسلسلي فارغ موجود مسبقاً إلى NULL.

from django.db import migrations, models


def empty_serials_to_null(apps, schema_editor):
    GrantItem = apps.get_model('grants', 'GrantItem')
    GrantItem.objects.filter(serial_number='').update(serial_number=None)


def noop(apps, schema_editor):
    # لا يمكن الرجوع بأمان: عدة أصناف بلا رقم تسلسلي لا يمكن إعادتها لنص فارغ مع شرط التفرّد.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0011_split_decision_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grantitem',
            name='serial_number',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name='الرقم التسلسلي'),
        ),
        migrations.RunPython(empty_serials_to_null, noop),
    ]
