# Generated by Django 5.1.1 on 2024-09-24 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("agreements", "0007_agreements_remaining_amount"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="agreements",
            name="remaining_amount",
        ),
    ]
