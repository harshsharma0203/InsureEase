from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InsuranceProductViewSet,
    PolicyApplicationViewSet,
    UnderwritingViewSet,
    PolicyViewSet,
    PolicyMemberViewSet,
    PolicyVersionViewSet
)

router = DefaultRouter()
router.register(r'products', InsuranceProductViewSet, basename='product')
router.register(r'applications', PolicyApplicationViewSet, basename='policy-application')
router.register(r'underwriting', UnderwritingViewSet, basename='underwriting')
router.register(r'policies', PolicyViewSet, basename='policy')
router.register(r'policy-members', PolicyMemberViewSet, basename='policy-member')
router.register(r'policy-versions', PolicyVersionViewSet, basename='policy-version')

urlpatterns = [
    path('', include(router.urls)),
]
