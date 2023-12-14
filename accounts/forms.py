# from datetime import datetime
# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.conf import settings

# from .models import CustomUser


# class CustomUserCreationForm(UserCreationForm):
#     _DEFAULT_DATE = datetime(2000, 1, 1).date()
#     date_of_birth = forms.DateField(
#         initial=_DEFAULT_DATE,
#         input_formats=settings.DATE_INPUT_FORMATS,
#         widget=forms.DateInput(attrs={'type': 'date'}, format=settings.DATE_INPUT_FORMATS[0]),
#     )
    
#     class Meta(UserCreationForm.Meta):
#         model = CustomUser
#         fields = ('first_name', 'last_name', 'email', 'gender', 'date_of_birth') #+ UserCreationForm.Meta.fields
