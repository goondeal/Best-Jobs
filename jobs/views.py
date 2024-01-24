from django.db.models import Count, F, Min, Max
from django.shortcuts import render, redirect, get_object_or_404
from .models import Job
from locations.models import *
from accounts.models import Company, CompanyInfo, Industry
from django.views.generic import ListView, DetailView


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
