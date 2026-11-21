from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EndorsementViewSet

router = DefaultRouter()
router.register(r'', EndorsementViewSet, basename='endorsement')

urlpatterns = [
    path('', include(router.urls)),
]
