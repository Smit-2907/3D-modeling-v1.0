"""
Centralized configuration for the Food-to-3D pipeline.
All paths, model settings, and server parameters are defined here.
"""

import os
from pathlib import Path

# ===== Base Directories =====
BASE_DIR = Path(__file__).parent.resolve()
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
MODELS_DIR = BASE_DIR / "models"
STATIC_DIR = BASE_DIR / "static"
LOG_DIR = BASE_DIR / "logs"

# Create directories on import
for d in [INPUT_DIR, OUTPUT_DIR, MODELS_DIR, STATIC_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ===== TripoSR Model Settings =====
TRIPOSR_MODEL_ID = "stabilityai/TripoSR"
TRIPOSR_CHUNK_SIZE = 8192
TRIPOSR_MC_RESOLUTION = 256  # High Quality as requested by the user
FOREGROUND_RATIO = 0.85
TEXTURE_RESOLUTION = 2048

# ===== Blender Settings =====
# Set this to your Blender executable path
# Common paths:
#   Windows: C:\Program Files\Blender Foundation\Blender 4.x\blender.exe
#   macOS:   /Applications/Blender.app/Contents/MacOS/Blender
#   Linux:   /usr/bin/blender or /snap/bin/blender
BLENDER_EXECUTABLE = os.environ.get(
    "BLENDER_PATH",
    r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
)

# ===== Server Settings =====
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# ===== Processing Settings =====
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_FILE_SIZE_MB = 20
MAX_POLY_COUNT = 50000  # Target polygon count for decimation

# ===== Logging =====
LOG_FORMAT = "%(asctime)s │ %(levelname)-8s │ %(name)-20s │ %(message)s"
LOG_LEVEL = "INFO"
