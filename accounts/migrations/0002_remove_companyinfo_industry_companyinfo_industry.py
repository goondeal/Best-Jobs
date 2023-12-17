# Generated by Django 5.0 on 2023-12-16 10:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyinfo',
            name='industry',
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='industry',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='companies', to='accounts.industry'),
            preserve_default=False,
        ),
    ]