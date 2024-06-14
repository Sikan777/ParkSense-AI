import os
import asyncio

import cv2
from datetime import datetime
import numpy as np
from keras.models import load_model

# The path to the XML file of the Haar cascade classifier and our model
CASCADE_ClASIFIER = 'DS/models/haarcascade_ua_license_plate.xml'
MODEL = 'DS/models/model_character_recognition.keras'

# Image saving format after processing
OUTPUT_FORMAT = 'png'

# license plate contour recognition coefficients
SCALE_FACTOR = 1.15
MIN_NEIGHBORS = 7

# coefficients of the contours of the symbols of the clipped license plate in the function detect_plate
WIDTH_LOWER = 1 / 10
WIDTH_UPPER = 2 / 3
HEIGH_LOWER = 1 / 10
HEIGH_UPPER = 3 / 5

model = load_model(MODEL, compile=False)
plate_cascade = cv2.CascadeClassifier(CASCADE_ClASIFIER)


async def detect_plate(img, text=''):
    """
    The function is designed for detecting and processing license plates in an image.

    Parameters:
    img (numpy.array): The image in which the license plates need to be detected and processed.
    text (str, optional): Text that can be added to the image around the license plate.

    Returns:
    numpy.array: The image with highlighted license plates and optionally added text.
    numpy.array or None: The image of the license plate area for further processing, or None if the license plate was not detected.
    """
    plate_img = img.copy()  # We copy the input image for processing
    roi = img.copy()  # Copy the input image to highlight the license plate area

    # Detection of license plates in the image
    plate_rect = plate_cascade.detectMultiScale(plate_img, scaleFactor=1.3, minNeighbors=8)

    # Initialize the plate variable before use
    plate = None

    # Processing of each license plate detected
    for (x, y, w, h) in plate_rect:
        # We extract the license plate area for further processing
        roi_ = roi[y:y + h, x:x + w, :]
        plate = roi[y:y + h, x:x + w, :]

        # We draw a rectangle around the license plate on the original image
        cv2.rectangle(plate_img, (x - 15, y), (x + w - 3, y + h - 5), (179, 206, 226), 3)

    # Adding text
    if text != '':
        plate_img = cv2.putText(plate_img, text, (15, 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        plate_img = cv2.putText(plate_img, text, (15, 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)

    # We return the processed image with selected license plates and the license plate area
    return plate_img, plate


async def find_contours(dimensions, img):
    """
    The function is designed for finding the contours of characters in a license plate image.

    Parameters:
        dimensions (list): A list containing the set of dimensions for the character contours:
                           lower_width, upper_width, lower_height, and upper_height.
        img (numpy.ndarray): The input image in which the character contours need to be found.

    Returns:
        numpy.ndarray: An array containing the image of character contours, sorted by the x-coordinate.
    """

    cntrs, _ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    lower_width = dimensions[0]
    upper_width = dimensions[1]
    lower_height = dimensions[2]
    upper_height = dimensions[3]

    cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:15]

    x_cntr_list = []
    target_contours = []
    img_res = []
    for cntr in cntrs:
        # Detect contour in binary image and return the coordinates of rectangle enclosing it
        intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)

        # Check the dimensions of the contour to filter out the characters by contour's size
        if intWidth > lower_width and intWidth < upper_width and intHeight > lower_height and intHeight < upper_height:
            x_cntr_list.append(
                intX)  # Store the x coordinate of the character's contour, to be used later for indexing the contours

            char_copy = np.zeros((44, 24))
            # Extract each character using the enclosing rectangle's coordinates
            char = img[intY:intY + intHeight, intX:intX + intWidth]
            char = cv2.resize(char, (20, 40))

            # Make result formatted for classification: invert colors
            char = cv2.subtract(255, char)

            # Resize the image to 24x44 with black border
            char_copy[2:42, 2:22] = char
            char_copy[0:2, :] = 0
            char_copy[:, 0:2] = 0
            char_copy[42:44, :] = 0
            char_copy[:, 22:24] = 0

            img_res.append(char_copy)  # List that stores the character's binary image (unsorted)
    indices = sorted(range(len(x_cntr_list)), key=lambda k: x_cntr_list[k])
    img_res_copy = []
    for idx in indices:
        img_res_copy.append(img_res[idx])  # Store character images according to their index
    img_res = np.array(img_res_copy)

    return img_res


async def segment_characters(image):
    """
    Finds characters in a license plate image.

    Parameters:
     - image: The license plate image from which characters will be extracted.

    Returns:
     - char_list: A list of character contours found in the image.
    """

    # We pre-process the license plate image
    img_lp = cv2.resize(image, (333, 75))
    img_gray_lp = cv2.cvtColor(img_lp, cv2.COLOR_BGR2GRAY)
    _, img_binary_lp = cv2.threshold(img_gray_lp, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img_binary_lp = cv2.erode(img_binary_lp, (3, 3))
    img_binary_lp = cv2.dilate(img_binary_lp, (3, 3))

    LP_WIDTH = img_binary_lp.shape[0]
    LP_HEIGHT = img_binary_lp.shape[1]

    # We make the borders white
    img_binary_lp[0:3, :] = 255
    img_binary_lp[:, 0:3] = 255
    img_binary_lp[72:75, :] = 255
    img_binary_lp[:, 330:333] = 255

    # Approximate dimensions of the contours of the symbols of the cropped license plate
    dimensions = [LP_WIDTH * WIDTH_LOWER,
                  LP_WIDTH * WIDTH_UPPER,
                  LP_HEIGHT * HEIGH_LOWER,
                  LP_HEIGHT * HEIGH_UPPER]

    char_list = await find_contours(dimensions, img_binary_lp)

    return char_list


async def fix_dimension(img):
    """
    Function for resizing an image to dimensions (28, 28, 3).

    Parameters:
    img (numpy.ndarray): The input image with dimensions (n, m), where n and m are integers.

    Returns:
    numpy.ndarray: An image with dimensions (28, 28, 3), where 3 is the number of channels (RGB).
    """

    new_img = np.zeros((28, 28, 3))
    for i in range(3):
        new_img[:, :, i] = img
    return new_img


async def show_results(char):
    """
    Function for displaying the results of character recognition on a license plate.

    Parameters:
    char (list): A list of license plate character images.

    Returns:
    str: A string containing the recognized license plate number, composed of individual characters.
    """

    dic = {}
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i, c in enumerate(characters):
        dic[i] = c

    output = []
    for i, ch in enumerate(char):  # we iterate over the symbols
        img_ = cv2.resize(ch, (28, 28), interpolation=cv2.INTER_AREA)
        img = await fix_dimension(img_)
        img = img.reshape(1, 28, 28, 3)  # image preparation for the model
        y_proba = model.predict(img, verbose=0)[0]  # we get probabilities for each class
        y_ = np.argmax(y_proba)  # we choose the class with the highest probability
        character = dic[y_]  # we get a symbol corresponding to the predicted class
        output.append(character)  # we save the result in the list

    plate_number = ''.join(output)  # we combine all symbols into a line

    return plate_number


async def plate_recognize(photo):
    """
    License plate recognition from an image.

    :param photo: Path to the image of the car with a license plate.
    :type photo: str
    :return: A tuple containing the image with a bounding box around the license plate and the recognized characters.
    :rtype: tuple
    """

    img = cv2.imread(photo)

    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # License plate detection in the image
    output_img, plate = await detect_plate(img, text=current_datetime_str)

    # Converting the image to the selected format
    _, img_buffer = cv2.imencode(f'.{OUTPUT_FORMAT}', output_img)
    img_bytes = img_buffer.tobytes()

    if plate is None:
        return img_bytes, None

    char = await segment_characters(plate)  # Identification of license plate symbols
    recognized_symbols = await show_results(char)  # Recognition of license plate symbols

    return img_bytes, recognized_symbols


async def main():
    """
    Recognizes license plates from images in 'DS/images/' directory, saves results and unrecognized plates.

    1. Retrieves a list of files in 'DS/images/' directory.
    2. Creates directories 'DS/results/' and 'DS/unrecognized/' for saving recognized and unrecognized plates, respectively.
    3. Iterates through each file in the directory.
    4. Calls plate_recognize() function to recognize the license plate.
    5. Saves the result if the license plate was recognized, otherwise saves the unrecognized plate.

    :return: None
    """
    # Getting a list of files in a directory DS/images/
    img_dir = 'DS/images/'
    img_files = os.listdir(img_dir)

    # Creation of a catalog for saving recognized signs
    results_dir = 'DS/results/'
    os.makedirs(results_dir, exist_ok=True)

    # Creating a directory to save unrecognized characters
    unrecognized_dir = 'DS/unrecognized/'
    os.makedirs(unrecognized_dir, exist_ok=True)

    # Go through each file in the directory
    for img_file in img_files:
        # The full path to the current file
        img_path = os.path.join(img_dir, img_file)

        # Call the plate_recognize() function to recognize the license plate
        result_img, recognized_symbols = await plate_recognize(img_path)

        # If the license plate was recognized, save the result
        if recognized_symbols:
            # A way to save the result
            result_filename = os.path.join(results_dir, f"{recognized_symbols}.jpg")
            cv2.imwrite(result_filename, result_img)
            print(f"Result for file {img_file} was preserved in {result_filename}")
        else:
            # If the license plate was not recognized, save it in the directory DS/unrecognized/
            unrecognized_filename = os.path.join(unrecognized_dir, img_file)
            cv2.imwrite(unrecognized_filename, result_img)
            print(f"Unrecognized character in file {img_file} was preserved in {unrecognized_filename}")

# # Running an asynchronous function main()
# asyncio.run(main())
