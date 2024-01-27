from django.contrib import admin
from .models import Job, JobApplication, JobQuestion, JobQuestionAnswer, JobApplicationAnswer


admin.site.register(Job)
admin.site.register(JobApplication)
admin.site.register(JobQuestion)
admin.site.register(JobQuestionAnswer)
admin.site.register(JobApplicationAnswer)
