# Generated by Django 3.2.7 on 2023-10-17 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20231017_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstats',
            name='biggest_loser_name',
            field=models.CharField(default=0.2, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userstats',
            name='biggest_winner_name',
            field=models.CharField(default=0.2, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userstats',
            name='biggest_loser',
            field=models.DecimalField(decimal_places=1, max_digits=12),
        ),
        migrations.AlterField(
            model_name='userstats',
            name='biggest_winner',
            field=models.DecimalField(decimal_places=1, max_digits=12),
        ),
    ]
