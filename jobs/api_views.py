"""
Django REST Framework API Views
Using beginner-friendly class-based views: ListAPIView, CreateAPIView, etc.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Resume, Job, JobApplication
from .serializers import (
    UserSerializer, LoginSerializer, ResumeSerializer,
    JobSerializer, JobApplicationSerializer
)
from .tasks import scrape_jobs_for_resume


# ============ Authentication APIs ============

class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Register a new user account
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Anyone can register
    
    def create(self, request, *args, **kwargs):
        # Validate and create user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate auth token for immediate login
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully!'
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """
    POST /api/auth/login/
    Login and get authentication token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Get or create token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Login successful!'
            })
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    """
    POST /api/auth/logout/
    Logout and delete authentication token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({
            'message': 'Logged out successfully!'
        })


class CurrentUserAPIView(generics.RetrieveAPIView):
    """
    GET /api/auth/me/
    Get current user information
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


# =============Resume APIs ============

class ResumeListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/resumes/ - List all resumes for logged-in user
    POST /api/resumes/ - Upload new resume
    """
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show resumes belonging to current user
        return Resume.objects.filter(user=self.request.user).order_by('-uploaded_at')
    
    def perform_create(self, serializer):
        # Save resume with auto-set user
        resume = serializer.save(user=self.request.user, task_status='pending')
        
        # Trigger background job scraping
        location = self.request.data.get('location', 'India')
        task = scrape_jobs_for_resume.delay(
            resume_id=resume.id,
            location=location,
            jobs_per_site=2
        )
        
        # Store task ID for status tracking
        resume.task_id = task.id
        resume.save()


class ResumeDetailAPIView(generics.RetrieveDestroyAPIView):
    """
    GET /api/resumes/{id}/ - Get resume details
    DELETE /api/resumes/{id}/ - Delete resume
    """
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only allow access to user's own resumes
        return Resume.objects.filter(user=self.request.user)


# ============ Job APIs ============

class JobListAPIView(generics.ListAPIView):
    """
    GET /api/jobs/ - List all jobs
    Supports filtering by: platform, resume_id, location
    """
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Base query: only show jobs from user's resumes
        queryset = Job.objects.filter(
            resume__user=self.request.user,
            is_active=True
        ).order_by('-scraped_at')
        
        # Optional filters from query params
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(platform=platform)
        
        resume_id = self.request.query_params.get('resume_id', None)
        if resume_id:
            queryset = queryset.filter(resume_id=resume_id)
        
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset


class JobDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/jobs/{id}/ - Get job details
    """
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Job.objects.filter(resume__user=self.request.user)


# ============ Application APIs ============

class ApplicationListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/applications/ - List all applications
    POST /api/applications/ - Create new application
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return JobApplication.objects.filter(
            job__resume__user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        # Validate that job belongs to user's resume
        job = serializer.validated_data['job']
        if job.resume.user != self.request.user:
            raise serializers.ValidationError(
                "You can only apply to jobs from your own resumes"
            )
        serializer.save()


class ApplicationUpdateAPIView(generics.UpdateAPIView):
    """
    PATCH /api/applications/{id}/ - Update application status
    PUT /api/applications/{id}/ - Full update
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return JobApplication.objects.filter(job__resume__user=self.request.user)
