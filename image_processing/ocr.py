import pytesseract
import cv2

def recognize_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Опціональна обробка зображення для поліпшення OCR
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    text = pytesseract.image_to_string(gray, config='--psm 8')
    return text.strip()
