import uvicorn
from dotenv import load_dotenv

load_dotenv()

from api.app import app

from configuration.config import (
    API_HOST,
    API_PORT,
    API_RELOAD,
)

if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
    )