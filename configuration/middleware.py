import time

from starlette.middleware.base import BaseHTTPMiddleware

from common.logger import logger
from configuration.context import RequestContext


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = RequestContext.generate_request_id()
        start_time = time.perf_counter()
        request_path = request.url.path

        logger.info(
            "[%s] Request started: %s %s",
            request_id,
            request.method,
            request_path,
        )

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            response.headers["X-Request-ID"] = request_id

            logger.info(
                "[%s] Request completed: %s %s | status=%s | duration=%.3fs",
                request_id,
                request.method,
                request_path,
                response.status_code,
                duration,
            )

            return response
        except Exception:
            duration = time.perf_counter() - start_time

            logger.exception(
                "[%s] Request failed: %s %s | duration=%.3fs",
                request_id,
                request.method,
                request_path,
                duration,
            )
            raise
