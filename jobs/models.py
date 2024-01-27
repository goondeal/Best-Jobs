from datetime import datetime
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from accounts.models import Company, User, Industry
from locations.models import City


class Skill(models.Model):
    name = models.CharField(max_length=155)

    def __str__(self) -> str:
        return self.name


class JobQuestion(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=255)
    required = models.BooleanField(default=False)

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
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=155)
    slug = models.SlugField(unique=True, allow_unicode=True, editable=False)
    _JOB_TYPES = (
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('FREELANCE_PROJECT', 'Freelance/Project'),
        ('SHIFT_BASED', 'Shift Based'),
        ('WORK_FROM_HOME', 'Work From Home'),
        ('VOLUNTEERING', 'Volunteering'),
    )
    type = models.CharField(max_length=155, choices=_JOB_TYPES)
    industry = models.ForeignKey(Industry, on_delete=models.PROTECT, related_name='jobs')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='jobs')
    _CAREER_LEVELS = (
        ('EXPERIENCED', 'Experienced Non-Manager'),
        ('MANAGER', 'Manager'),
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
    questions = models.ManyToManyField(JobQuestion, related_name='jobs')
    savers = models.ManyToManyField(User, related_name='saved_jobs', through='UserSavedJobs')

    keep_company_confidential = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['company'], name='job_company_index'),
            models.Index(fields=['city'], name='job_city_index')
        ]

    @property
    def location(self):
        return f'{self.city}, {self.city.state}, {self.city.state.country}'

    @property
    def get_job_type_str(self):
        for type in self._JOB_TYPES:
            if type[0] == self.type:
                return type[1]
        return self.type            

    @property
    def get_career_level_str(self):
        for level in self._CAREER_LEVELS:
            if level[0] == self.career_level:
                return level[1]
        return self.career_level            

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title, allow_unicode=True)
            if Job.objects.filter(slug=slug).exists():
                slug = slugify(f'{self.title} {self.company}', allow_unicode=True)
                while Job.objects.filter(slug=slug).exists():
                    random_num = str(datetime.now().timestamp()).split('.')[-1][-3:]
                    slug = slugify(f'{self.title} {self.company} {random_num}', allow_unicode=True)
            self.slug = slug
        super(Job, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.company} - {self.title}'    


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(max_length=2000, blank=True, null=True)
    # questions = models.ManyToManyField(JobQuestion, through='JobApplicationAnswer')
    cv = models.FileField(upload_to='applications_cvs', validators=[FileExtensionValidator(allowed_extensions=['txt', 'pdf', 'doc', 'docx'])])
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
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(JobQuestion, on_delete=models.CASCADE, related_name='application_answers')
    answer = models.CharField(max_length=155)
    
    def __str__(self) -> str:
        return f'APP-{self.application.id} {self.question} {self.answer}'

class UserSavedJobs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(fields=['job', 'user'], name='no_repeated_saved_jobs_for_users')
        ]

    def __str__(self) -> str:
        return f'{self.job} - {self.user}'    
