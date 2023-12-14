from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import Company, User
from locations.models import City


class JobCategory(models.Model):
    name = models.CharField(max_length=155)

    def __str__(self) -> str:
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=155)

    def __str__(self) -> str:
        return self.name


class JobQuestion(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=255)
    optional = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['company'], name='question_company_index'),
        ]

    def __str__(self) -> str:
        return self.question    


class JobQuestionAnswer(models.Model):
    question = models.ForeignKey(JobQuestion, on_delete=models.CASCADE, related_name='answers')
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['question'], name='answer_question_index'),
        ]

    def __str__(self) -> str:
        return self.value


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=155)
    _JOB_TYPES = (
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('FREELANCE_PROJECT', 'Freelance/Project'),
        ('SHIFT_BASED', 'Shift Based'),
        ('WORK_FROM_HOME', 'Work From Home'),
        ('VOLUNTEERING', 'Volunteering'),
    )
    type = models.CharField(max_length=155, choices=_JOB_TYPES)
    category = models.ManyToManyField(JobCategory, related_name='jobs')
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    _CAREER_LEVELS = (
        ('EXPERIENCED', 'Experienced Non-Manager'),
        ('Manager', 'Manager'),
        ('SENIOR', 'Senior'),
        ('MID_LEVEL', 'Mid-Level'),
        ('ENTRY_LEVEL', 'Entry-Level Junior/Fresh-Grad'),
        ('STUDENT', 'Student Undergrad/Postgrad'),
    )
    career_level = models.CharField(max_length=155, choices=_CAREER_LEVELS)
    min_years_of_experience = models.PositiveSmallIntegerField()
    max_years_of_experience = models.PositiveSmallIntegerField()
    salary_min = models.PositiveIntegerField()
    salary_max = models.PositiveIntegerField()
    show_salary = models.BooleanField(default=True)
    salary_additional_details = models.TextField(max_length=200, blank=True, null=True)
    num_of_vacancies = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], default=1)
    description = models.TextField(max_length=1000)
    requirements = models.TextField(max_length=1000)
    what_we_offer = models.TextField(max_length=1000, blank=True, null=True)
    skills = models.ManyToManyField(Skill, related_name='jobs')
    questions = models.ManyToManyField(JobQuestion, related_name='selected_questions')

    keep_company_confidential = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['company'], name='job_company_index'),
            models.Index(fields=['city'], name='job_city_index')
        ]

    def __str__(self) -> str:
        return f'{self.company} - {self.title}'    


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(max_length=2000, blank=True, null=True)
    answers = models.ManyToManyField(JobQuestionAnswer, through='JobApplicationAnswer')

    created_at = models.DateTimeField(auto_now_add=True)
    last_update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(fields=['job', 'user'], name='only_one_application_per_user')
        ]

    def __str__(self) -> str:
        return f'{self.job} - {self.user}'    


class JobApplicationAnswer(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    question = models.ForeignKey(JobQuestion, on_delete=models.CASCADE)
    answer = models.CharField()
    
    def __str__(self) -> str:
        return f'APP-{self.application.id} {self.question} {self.answer}'
