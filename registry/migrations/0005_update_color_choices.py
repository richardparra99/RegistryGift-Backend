from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0004_alter_event_color'),  # 👈 usa el nombre real de tu última migración
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='color',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('red', 'Rojo'),
                    ('blue', 'Azul'),
                    ('green', 'Verde'),
                    ('orange', 'Naranja'),
                    ('purple', 'Morado'),
                    ('yellow', 'Amarillo'),
                    ('pink', 'Rosa'),
                    ('gray', 'Gris'),
                    ('teal', 'Turquesa'),
                    ('brown', 'Marrón')
                ],
                default='red'
            ),
        ),
    ]
