import time
import schedule
from typing import Callable

class TaskScheduler:
    def __init__(self):
        self.scheduler = schedule.Scheduler()

    def add_store_recheck_schedule(self, interval_hours: int, task: Callable):
        self.scheduler.every(interval_hours).hours.do(task)

    def add_product_refresh_schedule(self, interval_minutes: int, task: Callable):
        self.scheduler.every(interval_minutes).minutes.do(task)

    def add_price_monitoring_schedule(self, interval_minutes: int, task: Callable):
        self.scheduler.every(interval_minutes).minutes.do(task)

    def run_pending(self):
        self.scheduler.run_pending()

    def start_loop(self, poll_interval: int = 1):
        while True:
            self.run_pending()
            time.sleep(poll_interval)