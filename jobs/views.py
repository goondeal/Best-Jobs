import json
from django.db.models import Count, F, Min, Max
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, RedirectView
from django.http import HttpResponse, JsonResponse
from .models import Job, JobApplicationAnswer, JobApplication
from locations.models import *
from accounts.models import Company, CompanyInfo, Industry, User
from .forms import JobApplicationForm, JobApplicationAnswerForm
from django.forms import formset_factory, modelform_factory, Select


def index(request):
    return redirect('country_jobs', country_code='eg')

def explore(request):
    return render(request, template_name='jobs/explore.html')

def country_jobs(request, country_code):
    country = get_object_or_404(Country, pk=country_code)
    jobs = Job.objects.filter(city__state__country__pk=country_code)
    country_top_companies = CompanyInfo.objects.filter(city__state__country__pk=country_code).order_by('-size')[:20]
    context = {
        'country': country,
        'jobs_count': jobs.count(),
        'top_companies': country_top_companies,
        'latest_jobs': jobs[:10],
        'job_categories': Industry.objects.all(),
        'locations': country.states.all()
    }
    return render(request, template_name='jobs/landing_page.html', context=context)

class JobsView(ListView):
    model = Job
    template_name = 'jobs/search_jobs.html'
    context_object_name = 'jobs'
    paginate_by = 30

    def _get_request_params(self):
        params = self.request.GET
        return {
            'q': params.get('q', ''),
            'countries': params.getlist('country'),
            'states': params.getlist('state'),
            'cities': params.getlist('city'),
            'min_yrs': params.get('min_years', '0'),
            'max_yrs': params.get('max_years'),
            'levels': params.getlist('level'),
            'categories': params.getlist('category'),
            'types': params.getlist('type'),
        }
    
    def _filter_queryset(self, queryset, **kwargs):
        result = queryset
        # filter by query
        q = kwargs.get('q')
        if q:
            result = result.filter(title__icontains=q)    
        # filter by level
        levels = kwargs.get('levels')
        if levels:
            result = result.filter(career_level__in=levels)
        # filter by years_of_exp
        min_yrs = kwargs.get('min_yrs')
        result = result.filter(min_years_of_experience__gte=min_yrs)
        max_yrs = kwargs.get('max_yrs')
        if max_yrs:
            result = result.filter(min_years_of_experience__lte=max_yrs)
        # filter by type
        types = kwargs.get('types')
        if types:
            result = result.filter(type__in=types)
        # filter by category
        categories = kwargs.get('categories')
        if categories:
            result = result.filter(industry__in=categories)
        
        # filter by location
        countries = kwargs.get('countries')
        states = kwargs.get('states')
        cities = kwargs.get('cities')
        if countries or states or cities:
            result = result.prefetch_related('city__state__country')
            if cities:
                result = result.filter(city__name__in=cities)
            elif states:
                result = result.filter(city__state__name__in=states)
            elif countries:
                result = result.filter(city__state__country__name__in=countries)
                
        return result

    def get_queryset(self):
        queryset = Job.objects.all()
        print('all jobs count', queryset.count())
        if self.request.method == 'GET':
            params = self._get_request_params()
            print('params =', params)
            queryset = self._filter_queryset(queryset, **params)
            print('jobs_count =', queryset.count())
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            queryset = Job.objects.all()
            # print('qs id =', id(queryset))
            params = self._get_request_params()
            
            # filter by all params except 'levels', then annotate by level
            filters = params.copy()
            filters.pop('levels', '')
            career_level_jobs = self._filter_queryset(queryset, **filters)\
                .values('career_level')\
                .annotate(jobs_count=Count('career_level'))\
                .filter(jobs_count__gt=0)\
                .order_by('-jobs_count')
            context['career_level_jobs'] = list(career_level_jobs)
            
            filters = params.copy()
            max_yrs_of_exp = self._filter_queryset(queryset, **filters)\
                .aggregate(years=Max('max_years_of_experience'))
            print('max_yrs_of_exp =', max_yrs_of_exp)
            context['years'] = range((max_yrs_of_exp.get('years') or 20) +1)

            # annotate by job category (industry)
            filters = params.copy()
            filters.pop('categories', '')
            categories_jobs = self._filter_queryset(queryset, **filters)\
                .prefetch_related('industry')\
                .values('industry__id', 'industry__name')\
                .annotate(id=F('industry__id'), name=F('industry__name'))\
                .annotate(jobs_count=Count('industry__name'))\
                .filter(jobs_count__gt=0)\
                .order_by('-jobs_count')
            context['categories'] = list(categories_jobs)
            
            # annotate by job type
            filters = params.copy()
            filters.pop('types', '')
            type_jobs = self._filter_queryset(queryset, **filters)\
                .values('type')\
                .annotate(jobs_count=Count('type'))\
                .filter(jobs_count__gt=0)\
                .order_by('-jobs_count')
            context['type_jobs'] = list(type_jobs)
            # print('type_jobs id =', id(type_jobs))

            # annotate by country
            filters = params.copy()
            countries = filters.pop('countries', [])
            states = filters.pop('states', [])
            filters.pop('cities', [])
            country_jobs = self._filter_queryset(queryset, **filters)\
                .prefetch_related('city__state__country')\
                .values('city__state__country__name')\
                .annotate(name=F('city__state__country__name'))\
                .annotate(jobs_count=Count('city__state__country__name'))\
                .filter(jobs_count__gt=0)\
                .order_by('-jobs_count')
            context['country_jobs'] = list(country_jobs)    
            # annotate by city
            city_jobs = self._filter_queryset(queryset, **filters)\
                .prefetch_related('city__state__country')\
                .filter(city__state__country__name__in=countries)\
                .values('city__state__name')\
                .annotate(name=F('city__state__name'))\
                .annotate(jobs_count=Count('city__state__name'))\
                .filter(jobs_count__gt=0)\
                .order_by('-jobs_count')
            context['city_jobs'] = list(city_jobs)
            print('list(city_jobs) =', list(city_jobs))    
            # annotate by area
            area_jobs = self._filter_queryset(queryset, **filters)\
                .prefetch_related('city__state__country')\
                .filter(city__state__country__name__in=countries)
            if states:
                area_jobs = area_jobs.filter(city__state__country__name__in=countries)
            area_jobs = area_jobs\
                .values('city__name')\
                .annotate(name=F('city__name'))\
                .annotate(jobs_count=Count('city__name'))\
                .filter(jobs_count__gt=0)\
                .order_by('-jobs_count')
            context['area_jobs'] = list(area_jobs)
            
        return context

class JobDetail(DetailView):
    model = Job

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()
        context['featured_jobs'] = Job.objects.filter(industry=job.industry)[:16]
        context['similar_jobs'] = Job.objects.filter(industry=job.industry)[:16]
        return context

class CompanyDetail(DetailView):
    model = CompanyInfo
    template_name = 'jobs/company_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # job = self.get_object()
        # context['featured_jobs'] = Job.objects.filter(industry=job.industry)[:16]
        # context['similar_jobs'] = Job.objects.filter(industry=job.industry)[:16]
        return context


@login_required
def saved(request):
    user = request.user
    if user.is_user:
        u = get_object_or_404(User, pk=user.id)
        if request.method == 'GET':
            context = {'jobs': u.saved_jobs.all()}
            return render(request, template_name='jobs/user_saved_jobs.html', context=context)
        elif request.method == 'POST':
            try:
                print('request body =', request.body)
                id = json.loads(request.body).get('id')
                job = get_object_or_404(Job, pk=id)
                print('job =', job)
                job_exists = u.saved_jobs.filter(pk=job.pk).exists()
                print('job_exists =', job_exists)
                if job_exists:
                    print('exists')
                    u.saved_jobs.remove(job)
                else:
                    print('not exists')
                    u.saved_jobs.add(job)
                return JsonResponse({'success': True})
            except:
                return JsonResponse({'success': False})
        else:
            return HttpResponse('Method Not Allowed')

    # request user is company
    return HttpResponse('Page Not Found', status=404)


@login_required
def applications(request, slug):
    user = request.user
    if user.is_user:
        u = get_object_or_404(User, pk=user.id)
        if request.method == 'GET':
            context = {'applications': u.applications.all()}
            return render(request, template_name='jobs/user_applications.html', context=context)
        else:
            return HttpResponse('Method Not Allowed')
    # request user is company
    return HttpResponse('Page Not Found', status=404)


@login_required
def job_application(request, slug):
    user = request.user
    if user.is_user:
        u = get_object_or_404(User, pk=user.id)
        job = get_object_or_404(Job, slug=slug)
        if request.method == 'GET':
            # check if Job is no longer open
            if not job.is_available:
                return HttpResponse('This job no longer accepts applications')
            # TODO: check if user had applied befor, return his application to edit
            formset = formset_factory(JobApplicationAnswerForm, extra=job.questions.count())
            # formset = formset_factory(JobApplicationAnswer, extra=job.selected_questions.count())
            # questions_form = []
            # for q in job.selected_questions.all():
            #     kwargs = {'fields': ['answer'], 'labels': {'answer': q.question}}
            #     if q.answers.exists():
            #         kwargs['widgets'] = {'answer': Select(choices={a.id: a.value for a in q.answers.all()}) }
            #     questions_form.append(
            #         modelform_factory(JobApplicationAnswer, **kwargs)
            #     )
            context = {'job': job, 'form': JobApplicationForm(), 'formset': formset}            
        elif request.method == 'POST':
            print('application request.POST =', request.POST)
            # TODO: save user application
            application_form = JobApplicationForm(request.POST, request.FILES)
            print('valid form =', application_form.is_valid())

            if application_form.is_valid():
                print('cleaned data =', application_form.cleaned_data)
                excluded_keys = set(application_form.cleaned_data.keys()).union({'csrfmiddlewaretoken'})
                keys = set(request.POST.keys()).difference(excluded_keys)
                print('keys =', keys)
                answers_forms = [
                    JobApplicationAnswerForm({'question': key, 'answer': request.POST.get(key)}) for key in keys
                ]
                if all([form.is_valid() for form in answers_forms]):
                    application = JobApplication.objects.create(
                        user=u,
                        job=job,
                        **application_form.cleaned_data
                    )
                    for form in answers_forms:
                        print('cleaned data =', form.cleaned_data)
                        JobApplicationAnswer.objects.create(
                            application=application,
                            **form.cleaned_data
                        )
                    return HttpResponse(f'Application was sent successfuly')
            else:
                print('errors =', application_form.errors)
            context = {'job': job, 'form': application_form, 'formset': None}
        else:
            return HttpResponse('Method Not Allowed')  
        return render(request, template_name='jobs/job_application.html', context=context)
    # request user is company
    return HttpResponse('Page Not Found', status=404)
