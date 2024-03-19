import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from redis.asyncio import Redis
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from api.v1.auth.router import router as auth_router
from api.v1.role.roles import router as role_router
from api.v1.role.user_roles import router as user_roles_router
from db.cache import redis_cache
from core.config import settings
from mock_data.create_user import create_test_users


@asynccontextmanager
async def lifespan(fast_api_app: FastAPI):
    async with Redis(
        host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True
    ) as redis_cache.cache_client:
        await create_test_users()
        yield


def configure_tracer() -> None:
    if not settings.activate_telemetry:
        return
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "auth-service"})))

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_host,
                agent_port=settings.jaeger_port,
            )
        )
    )

    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


tracer = trace.get_tracer(__name__)


def build_app():
    fast_api_app = FastAPI(
        title="Auth Sprint 1",
        description="Includes auth api and roles api",
        version="1.0.0",
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    fast_api_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fast_api_app.include_router(auth_router, prefix="/api/v1")
    fast_api_app.include_router(role_router, prefix="/api/v1")
    fast_api_app.include_router(user_roles_router, prefix="/api/v1")

    return fast_api_app


configure_tracer()
app = build_app()
FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})

    with trace.get_tracer(__name__).start_as_current_span(f"{request.method}: {request.url.path}") as span:
        span.set_attribute("http.request_id", request_id)
        jaeger_debug_id = request.headers.get("jaeger-debug-id")
        if jaeger_debug_id:
            span.set_attribute("jaeger-debug-id", jaeger_debug_id)

        response = await call_next(request)

    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.fastapi_host, port=settings.fastapi_port, reload=True)
