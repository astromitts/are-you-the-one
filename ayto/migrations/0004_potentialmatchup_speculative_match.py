# Generated by Django 3.1.4 on 2020-12-11 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayto', '0003_auto_20201211_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='potentialmatchup',
            name='speculative_match',
            field=models.BooleanField(default=False),
        ),
    ]
