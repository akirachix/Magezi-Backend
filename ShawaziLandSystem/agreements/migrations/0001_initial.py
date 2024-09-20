# Generated by Django 5.1.1 on 2024-09-19 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agreements',
            fields=[
                ('agreement_id', models.AutoField(primary_key=True, serialize=False)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('contract_duration', models.PositiveSmallIntegerField()),
                ('agreed_amount', models.PositiveIntegerField()),
                ('installment_schedule', models.TextField()),
                ('penalties_interest_rate', models.PositiveIntegerField()),
                ('down_payment', models.PositiveIntegerField()),
                ('buyer_agreed', models.BooleanField(default=False)),
                ('seller_agreed', models.BooleanField(default=False)),
                ('terms_and_conditions', models.TextField(default='No terms and conditions provided.')),
                ('transaction_count', models.PositiveIntegerField(default=0)),
                ('remaining_amount', models.FloatField(default=0.0)),
                ('total_amount_made', models.FloatField(default=0.0)),
                ('agreement_hash', models.CharField(blank=True, max_length=64)),
                ('previous_hash', models.CharField(blank=True, max_length=64, null=True)),
                ('transactions_history', models.JSONField(blank=True, default=list)),
            ],
        ),
    ]