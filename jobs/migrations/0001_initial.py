# Generated by Django 5.0 on 2023-12-16 02:31

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('locations', '0002_alter_city_state_alter_state_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=155)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=155)),
                ('type', models.CharField(choices=[('FULL_TIME', 'Full Time'), ('PART_TIME', 'Part Time'), ('FREELANCE_PROJECT', 'Freelance/Project'), ('SHIFT_BASED', 'Shift Based'), ('WORK_FROM_HOME', 'Work From Home'), ('VOLUNTEERING', 'Volunteering')], max_length=155)),
                ('career_level', models.CharField(choices=[('EXPERIENCED', 'Experienced Non-Manager'), ('MANAGER', 'Manager'), ('SENIOR', 'Senior'), ('MID_LEVEL', 'Mid-Level'), ('ENTRY_LEVEL', 'Entry-Level Junior/Fresh-Grad'), ('STUDENT', 'Student Undergrad/Postgrad')], max_length=155)),
                ('min_years_of_experience', models.PositiveSmallIntegerField()),
                ('max_years_of_experience', models.PositiveSmallIntegerField()),
                ('salary_min', models.PositiveIntegerField()),
                ('salary_max', models.PositiveIntegerField()),
                ('show_salary', models.BooleanField(default=True)),
                ('salary_additional_details', models.TextField(blank=True, max_length=200, null=True)),
                ('num_of_vacancies', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('description', models.TextField(max_length=1000)),
                ('requirements', models.TextField(max_length=1000)),
                ('what_we_offer', models.TextField(blank=True, max_length=1000, null=True)),
                ('keep_company_confidential', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_update_at', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locations.city')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.company')),
                ('industry', models.ManyToManyField(to='accounts.industry')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover_letter', models.TextField(blank=True, max_length=2000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_update_at', models.DateTimeField(auto_now=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='jobs.job')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='accounts.user')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='JobQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255)),
                ('optional', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='accounts.company')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='JobApplicationAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=155)),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.jobapplication')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.jobquestion')),
            ],
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='questions',
            field=models.ManyToManyField(through='jobs.JobApplicationAnswer', to='jobs.jobquestion'),
        ),
        migrations.AddField(
            model_name='job',
            name='questions',
            field=models.ManyToManyField(related_name='selected_questions', to='jobs.jobquestion'),
        ),
        migrations.CreateModel(
            name='JobQuestionAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='jobs.jobquestion')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddField(
            model_name='job',
            name='skills',
            field=models.ManyToManyField(related_name='jobs', to='jobs.skill'),
        ),
        migrations.AddIndex(
            model_name='jobquestion',
            index=models.Index(fields=['company'], name='question_company_index'),
        ),
        migrations.AddConstraint(
            model_name='jobapplication',
            constraint=models.UniqueConstraint(fields=('job', 'user'), name='only_one_application_per_user'),
        ),
        migrations.AddIndex(
            model_name='jobquestionanswer',
            index=models.Index(fields=['question'], name='answer_question_index'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['company'], name='job_company_index'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['city'], name='job_city_index'),
        ),
    ]
