from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import SignupView
from jobs.views import index, country_jobs, JobsView, JobDetail, CompanyDetail


urlpatterns = [
    # auth
    path('signup/', SignupView.as_view(), name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # jobs
    path('', index, name='index'),
    path('<str:country_code>/jobs', country_jobs, name='country_jobs'),
    path('jobs/<slug:slug>', JobDetail.as_view(), name='job_detail'),
    path('search', JobsView.as_view(), name='search_jobs'),
    path('saved', JobsView.as_view(), name='saved_jobs'),
    path('applications', JobsView.as_view(), name='applications'),
    path('companies/<slug:slug>', CompanyDetail.as_view(), name='company_detail'),

    # admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
