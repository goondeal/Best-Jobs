from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import SignupView


urlpatterns = [
    # auth
    path('signup/', SignupView.as_view(), name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),

    # admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
