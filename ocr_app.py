import streamlit as st
import pytesseract
import cv2
import numpy as np
from PIL import Image
import re

st.title("🪪 CNIC OCR Extractor")

st.markdown("Upload a CNIC image **or** take a photo using your camera:")

# Option 1: Upload from file
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

# Option 2: Use camera
camera_image = st.camera_input("Take a photo")

# Choose image source
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded CNIC", use_column_width=True)
elif camera_image:
    image = Image.open(camera_image)
    st.image(image, caption="Captured CNIC", use_column_width=True)
else:
    st.warning("📷 Upload an image or take a photo to proceed.")
    st.stop()

# Convert to OpenCV format
img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

# Preprocessing
gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
denoised = cv2.medianBlur(thresh, 3)

# OCR for alphabets (name)
text_alpha = pytesseract.image_to_string(
    denoised,
    config='--oem 3 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "'
)
alpha_lines = [line.strip() for line in text_alpha.split('\n') if line.strip()]

# OCR for CNIC
text_numeric = pytesseract.image_to_string(
    denoised,
    config='--oem 3 --psm 4 -c tessedit_char_whitelist="0123456789-"'
)
cnic_match = re.search(r'\d{5}-\d{7}-\d', text_numeric)
cnic_number = cnic_match.group() if cnic_match else "Not found"

# Name extraction
def clean_name(name_line):
    name_line = re.sub(r'[^a-zA-Z\s]', '', name_line)
    return re.sub(r'\s+', ' ', name_line).strip()

name = "Not found"
for i, line in enumerate(alpha_lines):
    if 'Name' in line and i + 1 < len(alpha_lines):
        raw_name = alpha_lines[i + 1]
        name = clean_name(raw_name)
        break
    elif i == 0:
        name = clean_name(line)

# Display results
st.markdown("### ✅ Extracted Info")
st.write(f"**Name:** {name}")
st.write(f"**CNIC:** {cnic_number}")
