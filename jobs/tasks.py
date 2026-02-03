"""
Celery Tasks for Job Scraping
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)



@shared_task(bind=True, max_retries=3)
def scrape_jobs_for_resume(self, resume_id, location='India', jobs_per_site=2):
    """
    Async task to scrape jobs across multiple platforms
    Runs in background so user gets instant response
    """
    from .models import Resume, Job
    from .scraper import JobScraperService, ResumeParser
    
    try:
        resume = Resume.objects.get(id=resume_id)
        
        # Update status to show processing has started
        resume.task_status = 'processing'
        resume.task_id = self.request.id
        resume.save()
        
        logger.info(f"Starting job scraping for resume {resume_id}")
        
        # Extract skills and keywords from resume file
        resume_path = resume.file.path
        keywords = ResumeParser.extract_keywords(resume_path)
        
        if not keywords:
            keywords = {'python', 'developer', 'intern'}
            logger.warning(f"No keywords found for resume {resume_id}, using defaults")
        
        # Save extracted keywords for display
        resume.keywords_extracted = ', '.join(keywords)
        resume.save()
        
        logger.info(f"Extracted keywords: {keywords}")
        
        # Initialize scraper service
        scraper_service = JobScraperService()
        
        # Scrape jobs from all platforms in parallel
        jobs_data = scraper_service.scrape_all_platforms(
            resume_path=resume_path,
            location=location,
            jobs_per_site=jobs_per_site
        )
        
        logger.info(f"Scraped {len(jobs_data)} jobs from all platforms")
        
        # Save jobs to database
        jobs_created = 0
        for job_data in jobs_data:
            try:
                # Avoid duplicates - check if job link already exists
                existing_job = Job.objects.filter(
                    link=job_data['link'],
                    resume=resume
                ).first()
                
                if not existing_job:
                    Job.objects.create(
                        resume=resume,
                        title=job_data['title'],
                        company=job_data['company'],
                        platform=job_data['platform'].lower().replace(' ', ''),
                        link=job_data['link'],
                        location=job_data.get('location', location),
                        scraped_at=timezone.now()
                    )
                    jobs_created += 1
            except Exception as e:
                logger.error(f"Error saving job: {e}")
                continue
        
        # Update resume with completion status
        resume.task_status = 'completed'
        resume.task_result = f'Successfully scraped {jobs_created} jobs'
        resume.save()
        
        logger.info(f"Task completed: Created {jobs_created} new jobs for resume {resume_id}")
        
        return {
            'status': 'success',
            'resume_id': resume_id,
            'jobs_created': jobs_created,
            'keywords': list(keywords),
            'message': f'Successfully scraped {jobs_created} jobs'
        }
        
    except Resume.DoesNotExist:
        logger.error(f"Resume {resume_id} not found")
        return {
            'status': 'error',
            'message': f'Resume {resume_id} not found'
        }
    
    except Exception as e:
        logger.error(f"Error in scrape_jobs_for_resume task: {e}", exc_info=True)
        
        # Update resume with error status
        try:
            resume = Resume.objects.get(id=resume_id)
            resume.task_status = 'failed'
            resume.task_result = f'Error: {str(e)}'
            resume.save()
        except:
            pass
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds


@shared_task
def cleanup_old_jobs():
    """
    Periodic task to clean up old job listings
    """
    from .models import Job
    from datetime import timedelta
    
    # Delete jobs older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = Job.objects.filter(scraped_at__lt=cutoff_date).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old jobs")
    return f"Deleted {deleted_count} old jobs"
