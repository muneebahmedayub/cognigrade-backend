import cv2
import numpy as np
from pyzbar import pyzbar
import os
from django.conf import settings
import random

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def correct_perspective(image):
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 1)
    edged = cv2.Canny(blur, 10, 70)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            screen_cnt = approx
            break
    else:
        return orig  
    warped = None
    try:
        rect = order_points(screen_cnt.reshape(4, 2))
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))
    except:
        return orig
    return warped

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)[1]
    return thresh

def decode_qr_code(image):
    qr_codes = pyzbar.decode(image)
    return qr_codes[0].data.decode("utf-8") if qr_codes else None

def detect_bubbles(processed_img, original_img, num_questions=30, options=4, columns=3, rows=10):
    height, width = processed_img.shape[:2]
    cell_width = width // columns
    cell_height = height // rows
    student_answers = []
    for col in range(columns):
        for row in range(rows):
            x_start = col * cell_width
            y_start = row * cell_height
            option_width = cell_width // (options + 1)
            candidates = []
            padding = 7
            for option in range(1, options + 1):
                ox_start = x_start + (option * option_width)
                ox_end = ox_start + option_width
                option_roi = processed_img[y_start+padding:y_start+cell_height-padding, ox_start+padding:ox_end-padding]
                filled_pixels = cv2.countNonZero(option_roi)
                total_pixels = option_roi.size
                if total_pixels == 0:
                    continue
                filled_ratio = filled_pixels / total_pixels
                if filled_ratio > 0.2:
                    candidates.append((filled_ratio, option))
            selected_answer = '?'
            if len(candidates) == 1:
                selected_answer = chr(64 + candidates[0][1]) 
            elif len(candidates) > 1:
                selected_answer = 'X'  
            student_answers.append(selected_answer)
    return student_answers

def grade_answers(student_answers, correct_answers):
    return sum(1 for s, c in zip(student_answers, correct_answers) if s == c)

def process_omr(image_path, correct_answers):
    try:
        original = cv2.imread(image_path)
        if original is None:
            raise FileNotFoundError("Image not found")
        corrected = correct_perspective(original)
        processed = preprocess_image(corrected)
        image_path = os.path.join(settings.MEDIA_ROOT, 'scanned-omr', f"{random.randint(1, 100000000)}.jpg")
        cv2.imwrite(image_path, processed)
        print(image_path)
        student_info = decode_qr_code(original)
        if not student_info:
            print("QR code not detected")
            # return
        answers = detect_bubbles(processed, corrected, num_questions=len(correct_answers))
        score = grade_answers(answers, correct_answers)
        print("\n" + "="*40)
        print(f" Student ID: {student_info}")
        print(f" Total Questions: {len(correct_answers)}")
        print(f" Correct Answers: {score}")
        print(f" Answer Sheet: {answers}")
        print("="*40 + "\n")

        return (score, answers)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return (0, [])
    
if __name__ == "__main__":
    CORRECT_ANSWERS = [
        'B', 'A', 'D', 'D', 'D', 'D', 'C', 'A', 'A', 'B',
        'A', 'D', 'A', 'A', 'C', 'D', 'A', 'B', 'C', 'D',
        'A', 'B', 'C', 'D', 'A', 'B', 'C', 'D', 'A', 'B']
    IMAGE_PATH = "DataSet/7.jpeg"
    process_omr(IMAGE_PATH, CORRECT_ANSWERS)
    cv2.waitKey(0)
