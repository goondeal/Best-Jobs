# Generated by Django 5.0 on 2024-01-26 21:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_rename_optional_jobquestion_required_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobapplication',
            name='questions',
        ),
        migrations.AlterField(
            model_name='job',
            name='questions',
            field=models.ManyToManyField(related_name='jobs', to='jobs.jobquestion'),
        ),
        migrations.AlterField(
            model_name='jobapplicationanswer',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='jobs.jobapplication'),
        ),
    ]