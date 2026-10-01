from fastapi import FastAPI

from app.api.routes import router
from app.api.v1.payments import router as payments_router

app = FastAPI(title="Legion Trade Router Spike")
app.include_router(router)
app.include_router(payments_router)
