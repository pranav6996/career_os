"""
Django REST Framework Serializers
Using beginner-friendly patterns for API data validation and serialization
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Resume, Job, JobApplication


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - used in registration and profile"""
    password = serializers.CharField(
        write_only=True,  # Never return password in API responses
        required=True,
        validators=[validate_password]  # Django's built-in password strength validation
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 
                  'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        """Ensure both passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create user with properly hashed password"""
        validated_data.pop('password2')  # Remove confirmation password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],  # Automatically hashed by create_user
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login - validates username and password"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class ResumeSerializer(serializers.ModelSerializer):
    """Serializer for Resume model"""
    user = serializers.StringRelatedField(read_only=True)  # Show username instead of ID
    job_count = serializers.SerializerMethodField()  # Computed field
    
    class Meta:
        model = Resume
        fields = ('id', 'user', 'file', 'uploaded_at', 'keywords_extracted',
                  'task_status', 'task_result', 'task_id', 'job_count')
        read_only_fields = ('uploaded_at', 'keywords_extracted', 'task_status',
                           'task_result', 'task_id')
    
    def get_job_count(self, obj):
        """Calculate number of jobs found for this resume"""
        return obj.job_set.count()


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model"""
    resume_id = serializers.IntegerField(read_only=True, source='resume.id')
    
    class Meta:
        model = Job
        fields = ('id', 'resume_id', 'title', 'company', 'platform', 'link',
                  'location', 'scraped_at', 'is_active')
        read_only_fields = ('scraped_at',)


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for JobApplication model"""
    job_title = serializers.CharField(read_only=True, source='job.title')
    job_company = serializers.CharField(read_only=True, source='job.company')
    
    class Meta:
        model = JobApplication
        fields = ('id', 'job', 'job_title', 'job_company', 'status', 
                  'applied_date', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_status(self, value):
        """Validate status choices"""
        valid_statuses = ['saved', 'applied', 'interviewing', 'rejected', 'accepted']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )
        return value
