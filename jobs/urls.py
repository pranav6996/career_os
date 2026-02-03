from django.urls import path
from . import views, api_views

app_name = 'jobs'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main URLs
    # Main pages
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Resume management
    path('upload/', views.upload_resume, name='upload_resume'),
    path('resumes/', views.resume_list, name='resume_list'),
    path('resumes/<int:resume_id>/rescrape/', views.rescrape_jobs, name='rescrape_jobs'),
    
    # Job listings
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/resume/<int:resume_id>/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    
    # Application management
    path('jobs/<int:job_id>/update-status/', views.update_application_status, name='update_application_status'),
]