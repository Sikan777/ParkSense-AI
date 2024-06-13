from fastapi import APIRouter

from typing import List
from datetime import datetime, timedelta
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import history as repositories_history
from src.schemas.history import HistoryUpdatePaid, HistoryGet, HistoryUpdateCar, HistoryUpdate, \
    HistorySchema
from src.entity.models import User, Role
from src.services.auth import auth_service


router = APIRouter(prefix="/history", tags=["History"])


@router.get("/create_entry/{find_plate}/{picture_id}", response_model=HistoryUpdate)
async def create_entry(find_plate, picture_id, session: AsyncSession = Depends(get_db)):
    history = await repositories_history.create_entry(find_plate, picture_id, session)
    if history is None:
        raise HTTPException(status_code=400, detail="Error creating entry car")
    return history


@router.get("/create_exit/{find_plate}/{picture_id}", response_model=HistoryUpdate)
async def create_exit(find_plate, picture_id, session: AsyncSession = Depends(get_db)):
    history = await repositories_history.create_exit(find_plate, picture_id, session)
    if history is None:
        raise HTTPException(status_code=400, detail="Error creating exit car")
    return history

@router.get()
async def namefunc():
    pass

@router.get()
async def namefunc():
    pass

@router.get()
async def namefunc():
    pass

@router.get()
async def namefunc():
    pass

@router.get()
async def namefunc():
    pass

