# Generated by Django 3.1 on 2022-07-08 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_remove_order_signature_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(max_length=100),
        ),
    ]
