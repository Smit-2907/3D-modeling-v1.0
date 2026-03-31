# 🍕 Food3D — AI-Powered Food Image to 3D Model Generator

Convert food photos into **AR-ready 3D models** (.glb) automatically using **TripoSR** AI + **Blender** post-processing.

> Upload image → AI generates 3D mesh → Blender optimizes → Download GLB → Use in AR

---

## ✨ Features

- **One-click 3D generation** — Upload a food photo, get a GLB model
- **TripoSR AI** — State-of-the-art single-image 3D reconstruction
- **Blender CLI** — Automated mesh optimization (smooth shading, decimation)
- **Three.js Viewer** — Interactive 3D preview with rotate, zoom, pan
- **FastAPI Backend** — RESTful API with background processing
- **WebAR Ready** — Optimized GLB output for AR integration
- **CLI Support** — Run the pipeline from terminal
- **Batch Processing** — Process multiple images at once

---

## 📦 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python + FastAPI |
| AI Model | TripoSR (Stability AI) |
| 3D Processing | Blender (CLI mode) |
| Frontend | HTML + CSS + JavaScript |
| 3D Viewer | Three.js |
| Package Manager | uv |

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.10+**
2. **[uv](https://docs.astral.sh/uv/)** — Fast Python package manager
3. **[Blender 4.x](https://www.blender.org/download/)** — For mesh → GLB conversion
4. **NVIDIA GPU** (recommended) — TripoSR runs on CPU too, but ~10x slower

### Install uv (if needed)

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup & Run

```bash
# 1. Clone / navigate to project
cd 3Dimages

# 2. Sync dependencies (creates .venv automatically)
uv sync

# 3. Configure Blender path (edit config.py or set env var)
set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

# 4. Start the server
uv run python app.py
```

Then open **http://localhost:8000** in your browser.

### Double-click to run (Windows)

Just run `run.bat` — it handles everything automatically.

---

## 🎮 Usage

### Web UI

1. Open http://localhost:8000
2. Drag & drop a food photo (or click to browse)
3. Click "Generate 3D Model"
4. Watch the progress in real-time
5. View the 3D model in the interactive viewer
6. Click "Download GLB" to save

### CLI

```bash
# Single image
uv run python pipeline.py path/to/food.jpg

# Multiple images
uv run python pipeline.py burger.png pizza.jpg sushi.webp

# With options
uv run python pipeline.py food.jpg --max-polys 30000 --verbose
```

### API

```bash
# Upload and generate
curl -X POST http://localhost:8000/generate-3d/ \
  -F "file=@food.jpg"

# Check status
curl http://localhost:8000/status/{job_id}

# Download model
curl -O http://localhost:8000/model/{job_id}

# List all jobs
curl http://localhost:8000/jobs
```

---

## 📁 Project Structure

```
3Dimages/
├── app.py                 # FastAPI server (main entry point)
├── pipeline.py            # Pipeline orchestrator (CLI + programmatic)
├── triposr_engine.py      # TripoSR AI model wrapper
├── convert_to_glb.py      # Blender CLI script (OBJ → GLB)
├── config.py              # Centralized configuration
├── pyproject.toml         # uv / Python project config
├── requirements.txt       # Pip-compatible dependencies
├── run.bat                # Windows quick-start script
├── .gitignore
├── README.md
│
├── static/
│   └── index.html         # Frontend UI with Three.js viewer
│
├── input/                 # Uploaded images (auto-created)
├── output/                # Generated models (auto-created)
├── models/                # Cached AI models (auto-created)
└── logs/                  # Processing logs (auto-created)
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `BLENDER_EXECUTABLE` | `C:\...\blender.exe` | Path to Blender |
| `SERVER_PORT` | `8000` | API server port |
| `MAX_POLY_COUNT` | `50000` | Target polygon count for GLB |
| `TRIPOSR_MC_RESOLUTION` | `256` | Marching cubes resolution (higher = more detail) |
| `MAX_FILE_SIZE_MB` | `20` | Max upload size |

Or set via environment variables:
```bash
set BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
```

---

## 🔧 Troubleshooting

### "Blender not found"
Update `BLENDER_PATH` in `config.py` or set the environment variable to your Blender installation path.

### "CUDA not available"
TripoSR will fall back to CPU automatically. Processing will be slower (~2-5 minutes vs ~30 seconds).

### "torchmcubes was not compiled with CUDA support"
```bash
uv pip uninstall torchmcubes
uv pip install git+https://github.com/tatsy/torchmcubes.git
```

### Model download is slow
The TripoSR model (~1.5GB) downloads from HuggingFace on first run. Subsequent runs use the cached model.

---

## 📜 License

MIT — Built with ❤️ using [TripoSR](https://github.com/VAST-AI-Research/TripoSR) by Stability AI & Tripo AI.
