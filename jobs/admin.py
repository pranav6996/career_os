from django.contrib import admin
from .models import Resume, Job, JobApplication


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'uploaded_at', 'keywords_preview']
    list_filter = ['uploaded_at']
    search_fields = ['keywords_extracted']
    date_hierarchy = 'uploaded_at'
    
    def keywords_preview(self, obj):
        if obj.keywords_extracted:
            keywords = obj.keywords_extracted.split(',')[:5]
            return ', '.join(keywords) + '...' if len(obj.keywords_extracted.split(',')) > 5 else ', '.join(keywords)
        return 'N/A'
    keywords_preview.short_description = 'Keywords'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'company', 'platform', 'location', 'scraped_at', 'is_active', 'view_link']
    list_filter = ['platform', 'is_active', 'scraped_at', 'location']
    search_fields = ['title', 'company', 'description']
    date_hierarchy = 'scraped_at'
    raw_id_fields = ['resume']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'company', 'platform', 'location')
        }),
        ('Links & Details', {
            'fields': ('link', 'description')
        }),
        ('Metadata', {
            'fields': ('resume', 'scraped_at', 'is_active')
        }),
    )
    
    def view_link(self, obj):
        from django.utils.html import format_html
        return format_html('<a href="{}" target="_blank">View Job</a>', obj.link)
    view_link.short_description = 'Job Link'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'job_title', 'job_company', 'status', 'applied_at', 'created_at']
    list_filter = ['status', 'created_at', 'applied_at']
    search_fields = ['job__title', 'job__company', 'notes']
    date_hierarchy = 'created_at'
    raw_id_fields = ['job']
    
    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'status', 'applied_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job Title'
    job_title.admin_order_field = 'job__title'
    
    def job_company(self, obj):
        return obj.job.company
    job_company.short_description = 'Company'
    job_company.admin_order_field = 'job__company'