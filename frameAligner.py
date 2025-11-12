import os
import cv2
import numpy as np

def color(text, col):
    codes = {
        "red": "91", "green": "92", "yellow": "93", "blue": "94",
        "magenta": "95", "cyan": "96", "bold": "1", "reset": "0"
    }
    return f"\033[{codes[col]}m{text}\033[0m"

# === Configuration ===
input_dir = "."
output_dir = "aligned_frames_interactive"
match_threshold = 0.7

# === Prompt for frame range ===
start_frame = int(input("Enter start frame number (e.g. 256): "))
end_frame = int(input("Enter end frame number (e.g. 961): "))
mid_frame = (start_frame + end_frame) // 2
reference_filename = f"frame_{mid_frame:05d}.jpg"

# === Setup ===
os.makedirs(output_dir, exist_ok=True)

# === Load reference image and interactively select template ===
reference_path = os.path.join(input_dir, reference_filename)
reference = cv2.imread(reference_path)
if reference is None:
    raise FileNotFoundError(f"Reference image not found: {reference_path}")

print("Select the sprocket hole in the reference image...")

# Resize for display
scale = 0.3
display_image = cv2.resize(reference, None, fx=scale, fy=scale)
roi = cv2.selectROI("Select sprocket hole", display_image)
cv2.destroyAllWindows()

# Scale ROI back up to full resolution
x, y, w, h = [int(r / scale) for r in roi]
TEMPLATE_X1, TEMPLATE_Y1 = x, y
TEMPLATE_X2, TEMPLATE_Y2 = x + w, y + h

print(f"Using template from ({TEMPLATE_X1}, {TEMPLATE_Y1}) to ({TEMPLATE_X2}, {TEMPLATE_Y2})")

# Convert reference to grayscale and extract template
gray_ref = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)
template = gray_ref[TEMPLATE_Y1:TEMPLATE_Y2, TEMPLATE_X1:TEMPLATE_X2]

if template is None or template.size == 0:
    raise ValueError("Invalid or empty template region.")

print(f"Template shape: {template.shape}, dtype: {template.dtype}")

# === Optional: Limit matching to the lower part of the image (bottom sprocket) ===
#SEARCH_Y1 = TEMPLATE_Y1 - 200 if TEMPLATE_Y1 - 200 > 0 else 0
#SEARCH_Y2 = TEMPLATE_Y2 + 200 if TEMPLATE_Y2 + 200 < reference.shape[0] else reference.shape[0]
SEARCH_Y1 = 1000
SEARCH_Y2 = 2464  # full image height

# === Build frame list ===
filenames = [
    f"frame_{i:05d}.jpg"
    for i in range(start_frame, end_frame + 1)
    if os.path.exists(os.path.join(input_dir, f"frame_{i:05d}.jpg"))
]

# === Alignment loop ===
for filename in filenames:
    input_path = os.path.join(input_dir, filename)
    color_image = cv2.imread(input_path)

    if color_image is None:
        print(f"Skipping {filename}: image failed to load.")
        continue

    gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

    # Define the search region within the grayscale image
    search_region = gray_image[SEARCH_Y1:SEARCH_Y2, :]

    # Match template in restricted region
    result = cv2.matchTemplate(search_region, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val < match_threshold:
        print(color(f"✗ Skipping {filename}: match too weak ({max_val:.3f})", "red"))
        continue

    # Translate match location back to full image coordinates
    match_x = max_loc[0]
    match_y = max_loc[1] + SEARCH_Y1

    # Calculate translation
    x_shift = match_x - TEMPLATE_X1
    y_shift = match_y - TEMPLATE_Y1

    # Apply shift to color image
    rows, cols = color_image.shape[:2]
    M = np.float32([[1, 0, -x_shift], [0, 1, -y_shift]])
    aligned = cv2.warpAffine(color_image, M, (cols, rows))

    # Save aligned image
    output_path = os.path.join(output_dir, filename)
    cv2.imwrite(output_path, aligned)
    #print(f"Aligned {filename} – match score: {max_val:.3f}, shift: ({x_shift}, {y_shift})")
    
    if max_val < match_threshold:
        print(color(f"✗ Skipping {filename}: match too weak ({max_val:.3f})", "red"))
        continue
    elif max_val < 0.90:
        print(color(f"⚠ Aligned {filename} – weak match ({max_val:.3f}), shift: ({x_shift}, {y_shift})", "yellow"))
    else:
        print(color(f"✓ Aligned {filename} – match: {max_val:.3f}, shift: ({x_shift}, {y_shift})", "green"))
