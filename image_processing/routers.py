from fastapi import APIRouter, UploadFile, File, HTTPException
from image_processing.detection import detect_license_plate
from image_processing.ocr import recognize_text
import shutil
import cv2

image_router = APIRouter(prefix="/image", tags=["image"])

@image_router.post("/process/")
async def process_image(file: UploadFile = File(...)):
    image_path = f"/tmp/{file.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    license_plate_image = detect_license_plate(image_path)
    if license_plate_image is None:
        raise HTTPException(status_code=404, detail="License plate not found")

    recognized_text = recognize_text(license_plate_image)
    
    return {"license_plate_text": recognized_text}
