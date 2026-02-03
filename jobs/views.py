from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Resume, Job, JobApplication
from .tasks import scrape_jobs_for_resume
import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import os

logger = logging.getLogger(__name__)


def index(request):
    """Home page showing recent jobs"""
    jobs = Job.objects.filter(is_active=True).select_related('resume')[:20]
    resumes = Resume.objects.all()[:5]
    
    context = {
        'jobs': jobs,
        'resumes': resumes,
        'total_jobs': Job.objects.count(),
        'total_resumes': Resume.objects.count(),
    }
    return render(request, 'jobs/index.html', context)


@require_http_methods(["GET", "POST"])
def upload_resume(request):
    """Upload resume and trigger job scraping"""
    if request.method == 'POST':
        if 'resume' not in request.FILES:
            messages.error(request, 'Please select a resume file')
            return redirect('jobs:upload_resume')
        
        resume_file = request.FILES['resume']
        location = request.POST.get('location', 'India')
        
        # Validate file type
        if not resume_file.name.endswith(('.pdf', '.docx')):
            messages.error(request, 'Please upload a PDF or DOCX file')
            return redirect('jobs:upload_resume')
        
        try:
            # Save resume
            resume = Resume.objects.create(
                file=resume_file,
                task_status='pending'
            )
            
            # Trigger Celery task for async job scraping
            from .tasks import scrape_jobs_for_resume
            task = scrape_jobs_for_resume.delay(
                resume_id=resume.id,
                location=location,
                jobs_per_site=2
            )
            
            # Save task ID
            resume.task_id = task.id
            resume.save()
            
            logger.info(f"Triggered job scraping task {task.id} for resume {resume.id}")
            
            messages.success(
                request, 
                'Resume uploaded successfully! Job scraping is in progress. '
                'Refresh the page to see results.'
            )
            return redirect('jobs:job_list', resume_id=resume.id)
        
        except Exception as e:
            logger.error(f"Error processing resume: {e}")
            messages.error(request, f'Error processing resume: {str(e)}')
            return redirect('jobs:upload_resume')
    
    return render(request, 'jobs/upload_resume.html')



def job_list(request, resume_id=None):
    """List all scraped jobs"""
    jobs_query = Job.objects.filter(is_active=True).select_related('resume')
    
    if resume_id:
        jobs_query = jobs_query.filter(resume_id=resume_id)
        resume = get_object_or_404(Resume, id=resume_id)
    else:
        resume = None
    
    # Filter by platform
    platform = request.GET.get('platform')
    if platform:
        jobs_query = jobs_query.filter(platform=platform)
    
    # Search
    search = request.GET.get('search')
    if search:
        jobs_query = jobs_query.filter(title__icontains=search) | jobs_query.filter(company__icontains=search)
    
    # Pagination
    paginator = Paginator(jobs_query, 10)
    page_number = request.GET.get('page', 1)
    jobs = paginator.get_page(page_number)
    
    context = {
        'jobs': jobs,
        'resume': resume,
        'platform': platform,
        'search': search,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, job_id):
    """View detailed job information"""
    job = get_object_or_404(Job.objects.select_related('resume'), id=job_id)
    
    # Get or create application
    application, created = JobApplication.objects.get_or_create(job=job)
    
    context = {
        'job': job,
        'application': application,
    }
    return render(request, 'jobs/job_detail.html', context)


@require_http_methods(["POST"])
def update_application_status(request, job_id):
    """Update job application status"""
    job = get_object_or_404(Job, id=job_id)
    application, created = JobApplication.objects.get_or_create(job=job)
    
    status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    
    if status in dict(JobApplication.STATUS_CHOICES):
        application.status = status
        application.notes = notes
        
        if status == 'applied' and not application.applied_at:
            from django.utils import timezone
            application.applied_at = timezone.now()
        
        application.save()
        messages.success(request, 'Application status updated!')
    else:
        messages.error(request, 'Invalid status')
    
    return redirect('jobs:job_detail', job_id=job_id)


def resume_list(request):
    """List all uploaded resumes"""
    resumes = Resume.objects.all()
    
    context = {
        'resumes': resumes,
    }
    return render(request, 'jobs/resume_list.html', context)


def dashboard(request):
    """Dashboard showing statistics"""
    total_jobs = Job.objects.count()
    total_resumes = Resume.objects.count()
    total_applications = JobApplication.objects.count()
    
    # Jobs by platform
    jobs_by_platform = {}
    for platform, name in Job.PLATFORM_CHOICES:
        count = Job.objects.filter(platform=platform).count()
        jobs_by_platform[name] = count
    
    # Recent jobs
    recent_jobs = Job.objects.filter(is_active=True).select_related('resume')[:5]
    
    # Application status breakdown
    application_stats = {}
    for status, label in JobApplication.STATUS_CHOICES:
        count = JobApplication.objects.filter(status=status).count()
        application_stats[label] = count
    
    context = {
        'total_jobs': total_jobs,
        'total_resumes': total_resumes,
        'total_applications': total_applications,
        'jobs_by_platform': jobs_by_platform,
        'recent_jobs': recent_jobs,
        'application_stats': application_stats,
    }
    return render(request, 'jobs/dashboard.html', context)


@require_http_methods(["POST"])
def rescrape_jobs(request, resume_id):
    """Re-scrape jobs for a specific resume"""
    resume = get_object_or_404(Resume, id=resume_id)
    location = request.POST.get('location', 'India')
    
    try:
        # Trigger Celery task for async job scraping
        from .tasks import scrape_jobs_for_resume
        task = scrape_jobs_for_resume.delay(
            resume_id=resume.id,
            location=location,
            jobs_per_site=2
        )
        
        # Update task status
        resume.task_id = task.id
        resume.task_status = 'pending'
        resume.save()
        
        logger.info(f"Triggered re-scraping task {task.id} for resume {resume_id}")
        messages.success(request, 'Re-scraping jobs in background. Refresh to see new results.')
        
    except Exception as e:
        logger.error(f"Error re-scraping jobs: {e}")
        messages.error(request, f'Error re-scraping: {str(e)}')
    
    return redirect('jobs:job_list', resume_id=resume_id)# Add to end of jobs/views.py

# ============ Authentication Views ============

def login_view(request):
    """Login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('jobs:index')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'jobs/login.html')


def signup_view(request):
    """Signup page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validation
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'jobs/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'jobs/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'jobs/signup.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Login automatically
        login(request, user)
        messages.success(request, f'Account created successfully! Welcome, {user.username}!')
        return redirect('jobs:index')
    
    return render(request, 'jobs/signup.html')


def logout_view(request):
    """Logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('jobs:login')
