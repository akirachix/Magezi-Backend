# Generated by Django 5.1.1 on 2024-09-23 04:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agreements", "0003_agreements_buyer_agreements_lawyer_agreements_seller"),
        ("transactions", "0003_remove_transactions_landdetail"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transactions",
            name="agreement",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transactions",
                to="agreements.agreements",
            ),
        ),
        migrations.AlterField(
            model_name="transactions",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Complete", "Complete"),
                    ("Rejected", "Rejected"),
                ],
                default="Pending",
                max_length=10,
            ),
        ),
    ]
