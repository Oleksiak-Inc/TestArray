import uvicorn
from app import create_app
from core.config import settings

app = create_app()

print("Starting app on", settings.SERVER_HOST, settings.SERVER_PORT)

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT
    )