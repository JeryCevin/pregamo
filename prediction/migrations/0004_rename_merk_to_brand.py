# Generated manually to rename merk field to brand

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prediction', '0003_cardataset'),
    ]

    operations = [
        # Rename field dan kolom database dari 'merk' ke 'brand'
        migrations.RenameField(
            model_name='cardataset',
            old_name='merk',
            new_name='brand',
        ),
    ]
