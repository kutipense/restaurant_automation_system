# Generated by Django 2.0.5 on 2018-05-07 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinerestaurant', '0003_auto_20180507_1249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='yemeksiparisi',
            name='onay',
        ),
        migrations.AddField(
            model_name='siparishavuzu',
            name='onay',
            field=models.BooleanField(default=False, verbose_name='Onay'),
        ),
    ]
