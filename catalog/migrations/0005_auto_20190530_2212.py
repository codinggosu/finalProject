# Generated by Django 2.1.5 on 2019-05-30 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20190530_2208'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rate',
            old_name='content',
            new_name='review',
        ),
    ]