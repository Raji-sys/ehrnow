from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "ROOT SITE"
admin.site.index_title = "EMR NOW"
admin.site.site_title = "ROOT SITE"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pathology/', include('pathology.urls',namespace='pathology')),
    path('pharm/', include('pharm.urls',namespace='pharm')),
    path('inventory/', include('inventory.urls',namespace='inventory')),
    path('',include('ehr.urls')),
    path('__reload__/', include('django_browser_reload.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
