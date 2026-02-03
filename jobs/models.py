from django.db import models
from django.utils import timezone


class Resume(models.Model):
    """Store uploaded resumes"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    keywords_extracted = models.TextField(blank=True, help_text="Comma-separated keywords")
    
    # Celery task tracking
    task_id = models.CharField(max_length=255, blank=True, null=True, help_text="Celery task ID")
    task_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    task_result = models.TextField(blank=True, help_text="Task result or error message")
    
    def __str__(self):
        return f"Resume {self.id} - {self.uploaded_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-uploaded_at']


class Job(models.Model):
    """Store scraped job listings"""
    
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('internshala', 'Internshala'),
        ('weworkremotely', 'WeWorkRemotely'),
        ('remoteok', 'RemoteOK'),
        ('naukri', 'Naukri'),
    ]
    
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=500)
    company = models.CharField(max_length=300)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    link = models.URLField(max_length=1000)
    location = models.CharField(max_length=200, default='India')
    description = models.TextField(blank=True, null=True)
    scraped_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} at {self.company} ({self.platform})"
    
    class Meta:
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['platform', '-scraped_at']),
            models.Index(fields=['resume', '-scraped_at']),
        ]


class JobApplication(models.Model):
    """Track job applications"""
    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('applied', 'Applied'),
        ('interviewing', 'Interviewing'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='saved')
    applied_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.job.title} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']