import logging
import os
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.db.models import *

from .routers import oidc
from .routers import init
from .routers import triggers


# setup loggers
# TODO: set config via env parameters...
logging_file_path = (Path(__file__).parent / "logging.conf").resolve()
logging.config.fileConfig(logging_file_path, disable_existing_loggers=False)

logger = logging.getLogger(__name__)

os.environ["TZ"] = settings.TIMEZONE
time.tzset()


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        # middleware=None,
    )
    return application


app = get_application()
app.include_router(oidc.router)
app.include_router(init.router)
app.include_router(triggers.router)

origins = settings.TRACTION_CORS_URLS.split(",")


@app.on_event("startup")
async def on_tenant_startup():
    """Register any events we need to respond to."""
    logger.warning(">>> Starting up app ...")


@app.on_event("shutdown")
def on_tenant_shutdown():
    """TODO no-op for now."""
    logger.warning(">>> Shutting down app ...")
    pass


@app.get("/", tags=["liveness"])
def main():
    return {"status": "ok", "health": "ok"}


if __name__ == "__main__":
    print("main.")
    uvicorn.run(app, host="0.0.0.0", port=5100)
