from pydantic import BaseModel, Field
from configuration.config import MAX_QUERY_LENGTH


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=MAX_QUERY_LENGTH,
        description="User query",
    )
    business_id: str = Field(
        ...,
        min_length=1,
        description="Business ID associated with the Knowledge Base",
    )
    course_ids: list[str] = Field(
        ...,
        min_length=1,
        description="Course IDs associated with the Knowledge Base",
    )