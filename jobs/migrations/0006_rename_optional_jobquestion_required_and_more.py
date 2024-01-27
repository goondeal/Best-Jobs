# Generated by Django 5.0 on 2024-01-26 09:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_usersavedjobs_job_savers_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobquestion',
            old_name='optional',
            new_name='required',
        ),
        migrations.AlterField(
            model_name='jobapplicationanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='application_answers', to='jobs.jobquestion'),
        ),
    ]
