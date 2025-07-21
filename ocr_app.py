from flask import Flask, request, jsonify
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io
import re

app = Flask(__name__)

@app.route('/')
def home():
    return 'OCR API is running!'

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    image = Image.open(file.stream).convert('RGB')
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Preprocessing
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.medianBlur(thresh, 3)

    # OCR: Name
    text_alpha = pytesseract.image_to_string(
        denoised,
        config='--oem 3 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "'
    )
    alpha_lines = [line.strip() for line in text_alpha.split('\n') if line.strip()]

    # OCR: CNIC
    text_numeric = pytesseract.image_to_string(
        denoised,
        config='--oem 3 --psm 4 -c tessedit_char_whitelist="0123456789-"'
    )
    cnic_match = re.search(r'\d{5}-\d{7}-\d', text_numeric)
    cnic = cnic_match.group() if cnic_match else "Not found"

    # Heuristic Name Extraction
    def clean(line):
        return re.sub(r'[^a-zA-Z\s]', '', line).strip()

    name = "Not found"
    for i, line in enumerate(alpha_lines):
        if 'Name' in line and i + 1 < len(alpha_lines):
            name = clean(alpha_lines[i + 1])
            break
        elif i == 0:
            name = clean(line)

    return jsonify({
        'name': name,
        'cnic': cnic
    })

if __name__ == '__main__':
    app.run()
