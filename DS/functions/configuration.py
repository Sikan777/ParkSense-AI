# The path to the XML file of the Haar cascade classifier and our model
CASCADE_ClASIFIER = 'DS/models/haarcascade_ua_license_plate.xml'
MODEL = 'DS/models/model_character_recognition.keras'

# Image saving format after processing
OUTPUT_FORMAT = 'png'

# license plate contour recognition coefficients
SCALE_FACTOR = 1.15
MIN_NEIGHBORS = 7

# coefficients of the contours of the symbols of the clipped license plate in the function detect_plate
WIDTH_LOWER = 1/10
WIDTH_UPPER = 2/3
HEIGH_LOWER = 1/10
HEIGH_UPPER = 3/5
