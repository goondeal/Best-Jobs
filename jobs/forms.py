from django.forms import ModelForm, Select
from django.core.exceptions import ValidationError
from .models import JobApplication, JobApplicationAnswer


class JobApplicationForm(ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'cv']
        help_texts = {
            'cv': 'txt, pdf, doc, or docx'
        }


class JobApplicationAnswerForm(ModelForm):
    class Meta:
        model = JobApplicationAnswer
        fields = ['question', 'answer']
    
    def clean(self):
        cleaned_data = super().clean()
        q = cleaned_data.get('question')
        a = cleaned_data.get('answer')
        if q.required and not a:
            raise ValidationError('this question is required')

