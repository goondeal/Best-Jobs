from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import login, authenticate

# from .forms import CustomUserCreationForm


class SignupView(View):
    template_name = 'accounts/signup.html'
    # form_class = CustomUserCreationForm
    
    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})
        
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
            )
            if user is not None:
                return redirect('login')
        return render(request, self.template_name, context={'form': form, 'message': 'Login failed!'})
