from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from .tasks import REGISTERED_TASKS

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    print(f"Loading {len(REGISTERED_TASKS)} scheduled tasks...")

    for task in REGISTERED_TASKS:
        try:
            scheduler.add_job(
                func = task.func,
                trigger = task.trigger,
                id = task.id,
                replace_existing = task.replace_existing,
                **task.options
            )
            print(f"✅ Task registered: {task.id} ({task.trigger})")

        except Exception as e:
             print(f"❌ Error registering task {task.id}: {e}")

    scheduler.start()
