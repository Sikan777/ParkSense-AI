import logging

import asynctempfile
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from DS.functions.image_process import plate_recognize
from src.database.db import get_db
from src.entity.models import User
from src.repository.history import create_entry, create_exit
from src.repository.image import create_image
from src.services.auth import auth_service
from src.services.cloud_service import cloud_service

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.post("/entry")
async def park_entry(user: User = Depends(auth_service.get_current_user), photo: UploadFile = File(...),
                     plate_number: str = Form(None), session: AsyncSession = Depends(get_db)) -> dict:
    # try:

    async with asynctempfile.NamedTemporaryFile(delete=False) as temp_file:
        await temp_file.write(await photo.read())
        file_path = temp_file.name

    img_processed, recognized_symbols = await plate_recognize(file_path)

    if not recognized_symbols and not plate_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="License plate not recognized and not entered manually")

    img_url, cloudinary_public_id = await cloud_service.upload_image(img_processed, 'Entry_photos')
    logging.info(img_url)

    picture = await create_image(session, recognized_symbols or plate_number, img_url, cloudinary_public_id)
    history = await create_entry(recognized_symbols or plate_number, picture.id, session)  # Виклик функції create_entry
    return {"message": "Welcome to Cars Home!", "image_url": img_url,
            "plate_number": recognized_symbols or plate_number}
    # #TODO create scheme
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@router.post("/exit")
async def park_exit(
        user: User = Depends(auth_service.get_current_user),
        photo: UploadFile = File(...),
        plate_number: str = Form(None),
        session: AsyncSession = Depends(get_db)
) -> dict:
    # try:
    async with asynctempfile.NamedTemporaryFile(delete=False) as temp_file:
        await temp_file.write(await photo.read())
        file_path = temp_file.name

    img_processed, recognized_symbols = await plate_recognize(file_path)

    if not recognized_symbols and not plate_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="License plate not recognized and not entered manually")

    img_url, cloudinary_public_id = await cloud_service.upload_image(img_processed, 'Exit_photos')

    picture = await create_image(session, recognized_symbols or plate_number, img_url, cloudinary_public_id)

    history = await create_exit(recognized_symbols or plate_number, picture.id, session)
    return {"message": "Have a good trip!", "image_url": img_url, "plate_number": recognized_symbols or plate_number}

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
