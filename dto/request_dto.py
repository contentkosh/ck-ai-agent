from pydantic import BaseModel, Field
from configuration.config import MAX_QUERY_LENGTH

class QueryRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        max_length=MAX_QUERY_LENGTH,
        description="User query",
    )