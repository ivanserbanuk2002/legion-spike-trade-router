from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.api.v1.payments import router as payments_router
from app.core.payments import InMemoryPaymentStore


def create_app(store: InMemoryPaymentStore | None = None) -> FastAPI:
    application = FastAPI(title="Legion Trade Router Spike")
    application.state.payment_store = store if store is not None else InMemoryPaymentStore()
    application.include_router(router)
    application.include_router(payments_router)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(_request, error: RequestValidationError):
        # Raw NaN/Infinity inputs cannot be serialized into a strict JSON response.
        details = [
            {key: item[key] for key in ("type", "loc", "msg")}
            for item in error.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": details})

    return application


app = create_app()
