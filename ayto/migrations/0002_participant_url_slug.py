# Generated by Django 3.1.4 on 2020-12-11 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayto', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='url_slug',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
