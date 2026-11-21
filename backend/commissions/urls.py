from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgentViewSet, CommissionViewSet

router = DefaultRouter()
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'', CommissionViewSet, basename='commission')

urlpatterns = [
    path('', include(router.urls)),
]
