from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="Legion Trade Router Spike")
app.include_router(router)
