# Generated by Django 5.1.1 on 2024-09-24 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agreements", "0008_remove_agreements_remaining_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="agreements",
            name="remaining_amount",
            field=models.PositiveIntegerField(default=0),
        ),
    ]