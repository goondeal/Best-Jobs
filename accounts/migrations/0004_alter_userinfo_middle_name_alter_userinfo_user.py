# Generated by Django 5.0 on 2024-01-24 03:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_companyinfo_foundation_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='middle_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='middle name'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounts.user'),
        ),
    ]
