# film-frame-aligner
A simple Python script for aligned scanned film, using CV with interactive GUI for selecting anchor points per batch
🎞️ Film Frame Aligner (frameAligner.py)

An interactive OpenCV-based tool that aligns scanned film frames by matching the sprocket hole region across images.
Designed for cinefilm digitisation workflows where consistent frame positioning is crucial before video assembly.



🚀 Features

Interactive ROI selection for the reference sprocket hole

Automatic alignment of all frames within a selected range

Configurable matching threshold

Coloured terminal feedback (✓ ⚠ ✗) for match quality

Preserves full-resolution alignment accuracy

Works on any sequentially numbered image set (frame_00001.jpg, etc.)

🧰 Requirements

Python 3.8+

OpenCV (cv2)

NumPy

Install dependencies:

pip install opencv-python numpy



📂 Usage

Place all your scanned frames in the same folder as fa9b.py.
Filenames must follow the pattern:

frame_00001.jpg
frame_00002.jpg
frame_00003.jpg
...


Run the script:

python frameAligner.py


When prompted, enter the start and end frame numbers
(for example, 256 and 961).

The script automatically picks the mid-frame as the reference and opens it in an OpenCV window.
Use your mouse to select the sprocket hole region and press Enter.

The program aligns all frames between the start and end numbers,
saving the results to:

aligned_frames_interactive/



⚙️ Configuration

Adjust these values near the top of the file if needed:

input_dir = "."
output_dir = "aligned_frames_interactive"
match_threshold = 0.7


You can also modify the search region:

SEARCH_Y1 = 1000
SEARCH_Y2 = 2464


These limit where template matching looks for sprockets (useful if only bottom holes are visible).



🖥️ Example output
✓ Aligned frame_00256.jpg – match: 0.935, shift: (-12, 5)
⚠ Aligned frame_00263.jpg – weak match (0.743), shift: (4, -1)
✗ Skipping frame_00277.jpg: match too weak (0.614)



🧩 How it works

Loads a reference frame and extracts a template from your selected sprocket hole area.

For each frame in range:

Converts to grayscale

Searches for the best template match within a defined region

Applies a translation transform (cv2.warpAffine) to align the image

Saves all aligned frames to the output folder.



🧠 Notes

This method assumes minimal rotation between frames.
If your film is warped or skewed, you may need an additional rotation correction stage.

Works best when the sprocket holes are consistently visible and well-lit.

You can refine alignment later with feature matching (ORB, ECC, etc.) if needed.

📜 License

MIT License — see LICENSE file for details.
