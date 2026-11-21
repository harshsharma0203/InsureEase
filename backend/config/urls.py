from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/groups/', include('groups.urls')),
    path('api/members/', include('members.urls')),
    path('api/', include('policy_management.urls')),
    path('api/endorsements/', include('endorsements.urls')),
    path('api/renewals/', include('renewals.urls')),
    path('api/claims/', include('claims.urls')),
    path('api/', include('billing.urls')),
    path('api/commissions/', include('commissions.urls')),
    path('api/reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
