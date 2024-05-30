from fastapi import FastAPI
from auth.routers import auth_router
from parking.routers import parking_router
from image_processing.routers import image_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(parking_router)
app.include_router(image_router)
