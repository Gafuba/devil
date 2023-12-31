# Generated by Django 3.2.7 on 2023-10-16 18:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0003_uservaluehistory_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uservaluehistory',
            name='name',
        ),
        migrations.CreateModel(
            name='CurrentValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cvalue', models.DecimalField(decimal_places=1, max_digits=12)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
