# Generated by Django 3.2.7 on 2023-11-13 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_itemprice_last_refresh'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemprice',
            name='first_sale_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
