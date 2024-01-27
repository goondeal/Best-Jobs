from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import SignupView
from jobs.views import index, country_jobs, JobsView, JobDetail, CompanyDetail, saved, applications, job_application


urlpatterns = [
    # auth
    path('signup/', SignupView.as_view(), name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # jobs
    path('', index, name='index'),
    path('<str:country_code>/jobs', country_jobs, name='country_jobs'),
    path('jobs/<slug:slug>', JobDetail.as_view(), name='job_detail'),
    path('jobs/<slug:slug>/apply', job_application, name='job_application'),
    path('search/', JobsView.as_view(), name='search_jobs'),
    path('saved/', saved, name='saved_jobs'),
    path('applications/', applications, name='user_applications'),
    path('companies/<slug:slug>', CompanyDetail.as_view(), name='company_detail'),
    path('companies/<slug:slug>/applications', CompanyDetail.as_view(), name='company_applications'),

    # admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
