# Generated by Django 3.1 on 2022-07-08 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contactus', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact_us',
            options={'verbose_name': 'contactus', 'verbose_name_plural': 'contact us'},
        ),
        migrations.RenameField(
            model_name='contact_us',
            old_name='subject',
            new_name='s',
        ),
    ]
