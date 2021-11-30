from typing import Callable

from datetime import timedelta

import schedule


def register_cron(fn: Callable[[], None], interval: timedelta) -> None:
    schedule.every(interval=interval.total_seconds()).seconds.do(fn)


def run_pending_cron_tasks() -> None:
    schedule.run_pending()
