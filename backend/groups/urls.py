from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InsuranceGroupViewSet

router = DefaultRouter()
router.register(r'', InsuranceGroupViewSet, basename='insurance-group')

urlpatterns = [
    path('', include(router.urls)),
]
