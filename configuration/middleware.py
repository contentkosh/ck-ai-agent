from starlette.middleware.base import BaseHTTPMiddleware

from configuration.context import RequestContext
from common.logger import logger


class RequestContextMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        request_id = RequestContext.generate_request_id()

        logger.info(
            f"[{request_id}] Incoming Request : "
            f"{request.method} {request.url.path}"
        )

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"[{request_id}] Request Completed"
        )

        return response