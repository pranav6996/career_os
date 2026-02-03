"""
API URL Configuration
"""
from django.urls import path
from jobs import api_views

app_name = 'api'

urlpatterns = [
    # Job endpoints
    path('jobs/', api_views.JobListCreateView.as_view(), name='job-list'),
    path('jobs/<int:pk>/', api_views.JobDetailView.as_view(), name='job-detail'),
    
    # Resume endpoints  
    path('resumes/', api_views.ResumeListCreateView.as_view(), name='resume-list'),
    path('resumes/<int:pk>/', api_views.ResumeDetailView.as_view(), name='resume-detail'),
    
    # Job scraping endpoint
    path('scrape/', api_views.TriggerJobScrapeView.as_view(), name='trigger-scrape'),
    
    # User registration
    path('register/', api_views.UserRegistrationView.as_view(), name='user-register'),
]
