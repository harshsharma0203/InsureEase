from django.urls import path
from .views import DashboardReportView, PolicyReportView, ClaimReportView, FinancialReportView

urlpatterns = [
    path('dashboard/', DashboardReportView.as_view(), name='report-dashboard'),
    path('policies/', PolicyReportView.as_view(), name='report-policies'),
    path('claims/', ClaimReportView.as_view(), name='report-claims'),
    path('financial/', FinancialReportView.as_view(), name='report-financial'),
]
