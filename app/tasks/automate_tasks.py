from app.celery_app import celery
from app.services.gem_scraper_service import run_gem_scraper

@celery.task(bind=True)
def run_gem_scraper_task(self, start_date, category):
    return run_gem_scraper(start_date, category)
