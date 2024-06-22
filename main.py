import asyncio
import os
from pathlib import Path
import uvicorn

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

# from src.services.telegram_sender import run_bot

from src.database.db import get_db
from src.routes import auth, users, history, image, parking, admin

app = FastAPI(title="ParkSense AI", description="Welcome to ParkSense AI API",
              swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

BASE_DIR = Path(__file__).parent
directory = BASE_DIR.joinpath("src").joinpath("static")
app.mount("/static", StaticFiles(directory=directory), name="static")

app.include_router(auth.router, prefix='/api', tags=['Authentication'])
app.include_router(users.router, prefix='/api', tags=['Users'])

app.include_router(admin.router, prefix='/api', tags=['Admin'])
app.include_router(image.router, prefix='/api', tags=['Images'])
app.include_router(parking.router, prefix='/api', tags=['Parking-Rate'])
app.include_router(history.router, prefix='/api', tags=['History'])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/healthchecker", tags=['Health checker'])
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(run_bot())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info")
