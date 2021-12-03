from typing import Callable

from datetime import timedelta

import schedule


def register_cron(fn: Callable[[], None], interval: timedelta) -> None:
    """
    Registers a cron task to run at a specified interval.

    Calling this function alone will not do anything. In order to run pending cron tasks, you must call
    `run_pending_cron_tasks` (the included management task `run_pending_cron_tasks` will do this for you on a loop)

    Args:
        fn: Function implementing the cron task.
        interval: Interval to run the cron task at.
    """
    schedule.every(interval=interval.total_seconds()).seconds.do(fn)


def run_pending_cron_tasks(all: bool = False) -> None:
    """
    Runs all pending cron tasks then returns.

    You usually won't want to call this – unless yu are implementing a custom clock process. In general, you'll want
    the management command `run_pending_cron_tasks`, which calls this for you on a loop.

    Args:
        all: Run all tasks regardless of whether they're scheduled
    """

    if all:
        schedule.run_all()
    else:
        schedule.run_pending()
