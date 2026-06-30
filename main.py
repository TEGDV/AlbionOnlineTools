import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from routers import api_items, api_compositions, views

# --- System Configuration ---
class PngLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return ".png" not in record.getMessage()

logging.getLogger("uvicorn.access").addFilter(PngLogFilter())

@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(InMemoryBackend())
    yield

# --- Application Initialization ---
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and data mounts
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

# Include Routers
app.include_router(api_items.router)
app.include_router(api_compositions.router)
app.include_router(views.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
