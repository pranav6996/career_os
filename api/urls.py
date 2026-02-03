"""
API URL Configuration
Routes for all REST API endpoints
"""
from django.urls import path
from jobs import api_views

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', api_views.RegisterAPIView.as_view(), name='register'),
    path('auth/login/', api_views.LoginAPIView.as_view(), name='login'),
    path('auth/logout/', api_views.LogoutAPIView.as_view(), name='logout'),
    path('auth/me/', api_views.CurrentUserAPIView.as_view(), name='current-user'),
    
    # Resume endpoints
    path('resumes/', api_views.ResumeListCreateAPIView.as_view(), name='resume-list-create'),
    path('resumes/<int:pk>/', api_views.ResumeDetailAPIView.as_view(), name='resume-detail'),
    
    # Job endpoints
    path('jobs/', api_views.JobListAPIView.as_view(), name='job-list'),
    path('jobs/<int:pk>/', api_views.JobDetailAPIView.as_view(), name='job-detail'),
    
    # Application endpoints
    path('applications/', api_views.ApplicationListCreateAPIView.as_view(), name='application-list-create'),
    path('applications/<int:pk>/', api_views.ApplicationUpdateAPIView.as_view(), name='application-update'),
]
