import streamlit as st
import pytesseract
from PIL import Image, ImageOps, ImageFilter
import numpy as np
import re

st.title("🪪 CNIC OCR Extractor")

st.markdown("Upload a CNIC image or take a photo using your camera:")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
camera_image = st.camera_input("Take a photo")

# Use whichever image is available
image = None
if uploaded_file:
    image = Image.open(uploaded_file)
elif camera_image:
    image = Image.open(camera_image)
else:
    st.warning("📷 Upload an image or take a photo to proceed.")
    st.stop()

st.image(image, caption="CNIC Image", use_column_width=True)

# Preprocessing (PIL-based)
gray = ImageOps.grayscale(image)
enhanced = gray.filter(ImageFilter.MedianFilter())
binary = enhanced.point(lambda x: 0 if x < 128 else 255, '1')

# OCR for alphabets (name)
text_alpha = pytesseract.image_to_string(
    binary,
    config='--oem 3 --psm 4 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "'
)
alpha_lines = [line.strip() for line in text_alpha.split('\n') if line.strip()]

# OCR for numbers (CNIC)
text_numeric = pytesseract.image_to_string(
    binary,
    config='--oem 3 --psm 4 -c tessedit_char_whitelist="0123456789-"'
)
cnic_match = re.search(r'\d{5}-\d{7}-\d', text_numeric)
cnic_number = cnic_match.group() if cnic_match else "Not found"

# Extract name
def clean_name(line):
    line = re.sub(r'[^a-zA-Z\s]', '', line)
    return re.sub(r'\s+', ' ', line).strip()

name = "Not found"
for i, line in enumerate(alpha_lines):
    if 'Name' in line and i + 1 < len(alpha_lines):
        name = clean_name(alpha_lines[i + 1])
        break
    elif i == 0:
        name = clean_name(line)

# Display results
st.markdown("### ✅ Extracted Info")
st.write(f"**Name:** {name}")
st.write(f"**CNIC:** {cnic_number}")
