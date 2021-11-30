from time import sleep

from django.core.management.base import BaseCommand

from pyck.core.cron import run_pending_cron_tasks


class Command(BaseCommand):
    help = "Background worker to run cron tasks"

    def handle(self, *args, **options):
        while True:
            run_pending_cron_tasks()
            sleep(30.0)
