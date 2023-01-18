from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

admin.site.site_header = 'files-transcriber | Admin console'

schema_view = get_schema_view(
    openapi.Info(
        title="Files Transcription API",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('superadmin/', admin.site.urls),
    path('', include('transcriber.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'docs(?P<format>\.json|\.yaml)/', schema_view.without_ui(cache_timeout=0), name='schema-json')
]

# For debug mode only
if settings.CONFIGURATION == 'dev':
    # Turn on debug toolbar
    import debug_toolbar

    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
