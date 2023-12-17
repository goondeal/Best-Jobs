from django.shortcuts import render, get_object_or_404
from .models import Job
from locations.models import Country


def index():
    return render('jobs/index.html')


def country_jobs(request, country_code):
    country = get_object_or_404(Country, pk=country_code)
    jobs_count = Job.objects.filter(city_state_country__pk=country_code)
    context = {
        country: country,
        jobs_count: jobs_count
    }
    return render(request, template_name='jobs/index.html', context=context)