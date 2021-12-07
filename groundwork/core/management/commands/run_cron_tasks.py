from time import sleep

from django.core.management.base import BaseCommand, CommandParser

from groundwork.core.cron import run_pending_cron_tasks


class Command(BaseCommand):
    help = "Background worker to run cron tasks"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run all registered tasks once, then exit",
        )

    def handle(self, *args, once, **options):
        if once:
            run_pending_cron_tasks(all=True)
            return

        while True:
            run_pending_cron_tasks()
            sleep(30.0)
