"""
Application Request Context
"""

import uuid
from contextvars import ContextVar


# ==========================================================
# Context Variable
# ==========================================================

request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default=None
)


# ==========================================================
# Request Context
# ==========================================================

class RequestContext:

    def __init__(self):

        request_id = request_id_context.get()

        if request_id is None:

            request_id = self.generate_request_id()

        self.request_id = request_id

    @staticmethod
    def generate_request_id():

        request_id = str(uuid.uuid4())

        request_id_context.set(request_id)

        return request_id

    @staticmethod
    def get_request_id():

        return request_id_context.get()