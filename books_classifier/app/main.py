import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from app.api.api import config_routers
from app.config import settings
from app.da_log import logger


def add_all_routers(app: FastAPI) -> None:
    app.include_router(
        config_routers(),
    )


def add_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def app_factory() -> FastAPI:
    app = FastAPI(
        title=settings.SERVICE_TITLE,
        description=settings.SERVICE_DESCRIPTION,
        version=settings.SERVICE_VERSION,
    )
    add_all_routers(app)
    add_middleware(app)
    return app


def run_server(log_config: Dict[str, Any]) -> None:
    uvicorn.run(
        settings.RUN_SERVER_COMMAND,
        host=settings.RUN_SERVER_HOST,
        port=settings.RUN_SERVER_PORT,
        access_log=settings.RUN_SERVER_ACCESS_LOG,
        log_level=settings.RUN_SERVER_LOG_LEVEL,
        factory=settings.RUN_SERVER_FACTORY,
        reload=settings.RUN_SERVER_DEBUG_RELOAD,
        log_config=log_config,
    )


if __name__ == "__main__":
    run_server(log_config=logger.get_log_config())
