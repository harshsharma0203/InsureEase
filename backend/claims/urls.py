from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClaimViewSet,
    ClaimDocumentViewSet,
    ClaimAssessmentViewSet,
    ClaimSettlementViewSet
)

router = DefaultRouter()
router.register(r'documents', ClaimDocumentViewSet, basename='claim-document')
router.register(r'assessments', ClaimAssessmentViewSet, basename='claim-assessment')
router.register(r'settlements', ClaimSettlementViewSet, basename='claim-settlement')
router.register(r'', ClaimViewSet, basename='claim')

urlpatterns = [
    path('', include(router.urls)),
]
