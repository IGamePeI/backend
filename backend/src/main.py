from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi.middleware import SlowAPIMiddleware

from api import main_router
from crud import init_db
from utils.modules.limiter import limiter
from utils.modules.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    await init_redis()
    yield
    await close_redis()


app: FastAPI = FastAPI(lifespan=lifespan, title="MyAPI")
app.include_router(main_router)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8090",
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:9090",
        "http://localhost:9080",
        "http://localhost:80",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


instrumentator: Instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=False,
)
instrumentator.instrument(
    app,
    metric_namespace="fastapi",
    metric_subsystem="",
).expose(app, endpoint="/metrics", tags=["Metrics"])


if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, use_colors=False, host="0.0.0.0", port=8090)
