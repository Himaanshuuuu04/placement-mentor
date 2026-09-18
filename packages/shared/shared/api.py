
from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware
from shared.logging import setup_logging
from shared.errors import global_exception_handler
from shared.observability import router as health_router

def create_app(service_name: str) -> FastAPI:
    setup_logging()
    app = FastAPI(title=service_name)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_exception_handler(Exception, global_exception_handler)
    app.include_router(health_router)
    return app
