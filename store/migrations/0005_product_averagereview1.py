# Generated by Django 3.1 on 2022-07-08 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_productgallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='averageReview1',
            field=models.FloatField(blank=True, default=0),
        ),
    ]
