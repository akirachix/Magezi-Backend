# Generated by Django 5.1.2 on 2024-10-11 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('land_sellers', '0004_landseller_landdetail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='landseller',
            name='LandDetail',
        ),
    ]