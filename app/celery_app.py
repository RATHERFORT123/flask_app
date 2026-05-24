# from celery import Celery

# celery = Celery(
#     "automation",
#     broker="redis://localhost:6379/0",
#     backend="redis://localhost:6379/0",
#     include=["app.tasks.automate_tasks"]
# )



from celery import Celery

celery = Celery(
    "automation",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.tasks.automate_tasks"]
)
