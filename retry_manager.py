import time
import math
from typing import Callable, Any

class RetryManager:
    def __init__(self, max_attempts: int = 3, base_backoff_sec: float = 2.0):
        self.max_attempts = max_attempts
        self.base_backoff_sec = base_backoff_sec

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        attempt = 0
        while attempt < self.max_attempts:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt >= self.max_attempts:
                    self.record_failure(func.__name__, str(e), kwargs)
                    raise e
                
                sleep_time = self.base_backoff_sec * math.pow(2, attempt - 1)
                time.sleep(sleep_time)

    def record_failure(self, func_name: str, error_msg: str, context: dict):
        failure_log = {
            "function": func_name,
            "error": error_msg,
            "context": context,
            "timestamp": time.time()
        }
        # Failed records saving logic (e.g., logging to file or DB)
        with open("failed_jobs.log", "a") as f:
            f.write(str(failure_log) + "\n")