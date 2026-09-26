import multiprocessing
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

from common.logger import logger
from configuration.constants import (
    QUERY_CANCEL_REJECTED_LOG,
    QUERY_CANCEL_REQUESTED_LOG,
    QUERY_JOB_CANCELLED_LOG,
    QUERY_JOB_COMPLETED_LOG,
    QUERY_JOB_CREATED_LOG,
    QUERY_JOB_FAILED_LOG,
    QUERY_JOB_STARTED_LOG,
)
from services.kb_query_service import ask_question

QUEUED = "queued"
RUNNING = "running"
COMPLETED = "completed"
CANCELLED = "cancelled"
FAILED = "failed"


@dataclass
class QueryJob:
    job_id: str
    query: str
    business_id: str
    course_ids: List[str]
    process: Optional[multiprocessing.Process] = None
    result_queue: Any = None
    status: str = QUEUED
    result: Any = None
    error: Optional[str] = None
    done_event: threading.Event = field(default_factory=threading.Event)
    lock: threading.Lock = field(default_factory=threading.Lock)


def _query_worker(
    job_id: str,
    query: str,
    business_id: str,
    course_ids: List[str],
    result_queue,
):
    try:
        result = ask_question(
            query=query,
            business_id=business_id,
            course_ids=course_ids,
            job_id=job_id,
        )

        result_queue.put(
            {
                "job_id": job_id,
                "status": COMPLETED,
                "result": result,
            }
        )

    except Exception as exception:
        result_queue.put(
            {
                "job_id": job_id,
                "status": FAILED,
                "error": str(exception),
            }
        )


class QueryJobManager:
    def __init__(self):
        self.jobs: Dict[str, QueryJob] = {}
        self.jobs_lock = threading.Lock()

    def create_job(
        self,
        query: str,
        business_id: str,
        course_ids: List[str],
    ) -> str:
        job_id = str(uuid4())
        result_queue = multiprocessing.Queue()

        job = QueryJob(
            job_id=job_id,
            query=query,
            business_id=business_id,
            course_ids=course_ids,
            result_queue=result_queue,
        )

        process = multiprocessing.Process(
            target=_query_worker,
            args=(
                job_id,
                query,
                business_id,
                course_ids,
                result_queue,
            ),
            daemon=True,
        )

        job.process = process

        with self.jobs_lock:
            self.jobs[job_id] = job

        logger.info(QUERY_JOB_CREATED_LOG, job_id)

        process.start()

        with job.lock:
            if job.status == QUEUED:
                job.status = RUNNING

        logger.info(QUERY_JOB_STARTED_LOG, job_id)

        threading.Thread(
            target=self._collect_result,
            args=(job_id,),
            daemon=True,
        ).start()

        return job_id

    def _collect_result(self, job_id: str):
        job = self.get_job(job_id)

        if job is None:
            return

        try:
            message = job.result_queue.get()

            with job.lock:
                if job.status == CANCELLED:
                    return

                if message["status"] == COMPLETED:
                    job.result = message["result"]
                    job.status = COMPLETED
                    logger.info(QUERY_JOB_COMPLETED_LOG, job_id)

                elif message["status"] == FAILED:
                    job.error = message.get("error")
                    job.status = FAILED
                    logger.error(
                        QUERY_JOB_FAILED_LOG,
                        job_id,
                        job.error,
                    )

        except Exception as exception:
            with job.lock:
                if job.status != CANCELLED:
                    job.status = FAILED
                    job.error = str(exception)
                    logger.error(
                        QUERY_JOB_FAILED_LOG,
                        job_id,
                        job.error,
                    )

        finally:
            job.done_event.set()

            if job.process and job.process.is_alive():
                job.process.join(timeout=0.1)

            try:
                job.result_queue.close()
            except Exception:
                pass

    def wait_for_result(self, job_id: str):
        job = self.get_job(job_id)

        if job is None:
            return None

        job.done_event.wait()

        with job.lock:
            if job.status == COMPLETED:
                return job.result

            return None

    def stop_job(self, job_id: str) -> bool:
        job = self.get_job(job_id)

        if job is None:
            return False

        with job.lock:
            if job.status in {
                COMPLETED,
                CANCELLED,
                FAILED,
            }:
                logger.info(
                    QUERY_CANCEL_REJECTED_LOG,
                    job_id,
                    job.status,
                )
                return False

            job.status = CANCELLED

        logger.info(
            QUERY_CANCEL_REQUESTED_LOG,
            job_id,
        )

        process = job.process

        if process and process.is_alive():
            process.terminate()
            process.join(timeout=2)

        job.done_event.set()

        logger.info(
            QUERY_JOB_CANCELLED_LOG,
            job_id,
        )

        return True

    def get_job(
        self,
        job_id: str,
    ) -> Optional[QueryJob]:
        with self.jobs_lock:
            return self.jobs.get(job_id)

    def get_status(
        self,
        job_id: str,
    ) -> Optional[Dict[str, Any]]:
        job = self.get_job(job_id)

        if job is None:
            return None

        with job.lock:
            return {
                "job_id": job.job_id,
                "status": job.status,
                "result": job.result,
                "error": job.error,
            }


query_job_manager = QueryJobManager()
