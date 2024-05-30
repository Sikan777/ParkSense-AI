import cv2

def detect_license_plate(image_path: str):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Використання каскадного класифікатора для виявлення номерних знаків
    plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')
    plates = plate_cascade.detectMultiScale(gray, 1.1, 10)

    for (x, y, w, h) in plates:
        license_plate_image = image[y:y+h, x:x+w]
        return license_plate_image
    
    return None
