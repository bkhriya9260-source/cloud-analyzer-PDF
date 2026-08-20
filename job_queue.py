import time
import json
import uuid
import redis
from enum import Enum
from typing import Dict, Any, Optional

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobQueue:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.queue_key = "queue:jobs"
        self.failed_queue_key = "queue:failed_jobs"

    def enqueue_job(self, job_type: str, payload: Dict[str, Any], max_retries: int = 3) -> str:
        job_id = str(uuid.uuid4())
        job_data = {
            "id": job_id,
            "type": job_type,
            "payload": payload,
            "status": JobStatus.PENDING.value,
            "retries": 0,
            "max_retries": max_retries,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        self.r.hset(f"job:{job_id}", mapping={"data": json.dumps(job_data)})
        self.r.lpush(self.queue_key, job_id)
        return job_id

    def process_next_job(self, handler_func):
        job_id = self.r.rpop(self.queue_key)
        if not job_id:
            return None

        job_key = f"job:{job_id}"
        raw_data = self.r.hget(job_key, "data")
        if not raw_data:
            return None

        job = json.loads(raw_data)
        job["status"] = JobStatus.PROCESSING.value
        job["updated_at"] = time.time()
        self.r.hset(job_key, "data", json.dumps(job))

        try:
            handler_func(job["type"], job["payload"])
            job["status"] = JobStatus.COMPLETED.value
            job["updated_at"] = time.time()
            self.r.hset(job_key, "data", json.dumps(job))
        except Exception as e:
            job["retries"] += 1
            job["updated_at"] = time.time()
            if job["retries"] <= job["max_retries"]:
                job["status"] = JobStatus.PENDING.value
                self.r.hset(job_key, "data", json.dumps(job))
                self.r.lpush(self.queue_key, job_id)
            else:
                job["status"] = JobStatus.FAILED.value
                job["error"] = str(e)
                self.r.hset(job_key, "data", json.dumps(job))
                self.r.lpush(self.failed_queue_key, job_id)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        raw_data = self.r.hget(f"job:{job_id}", "data")
        return json.loads(raw_data) if raw_data else None