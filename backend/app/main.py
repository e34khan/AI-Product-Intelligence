from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="AI Product Intelligence")
app.include_router(router)
