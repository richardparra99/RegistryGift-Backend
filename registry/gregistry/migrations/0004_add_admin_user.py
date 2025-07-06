from django.db import migrations


def insertData(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')

    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            username='admin',
            password='1234',
            email='admin@admin.com'
        )
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()

    admin_group, _ = Group.objects.get_or_create(name='Administrador')
    admin_user.groups.add(admin_group)


class Migration(migrations.Migration):

    dependencies = [
        ('gregistry', '0003_add_permissions'),
    ]

    operations = [
        migrations.RunPython(insertData, atomic=True),
    ]

