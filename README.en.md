# stream-clipper

A Python-based CLI tool designed to automatically detect chat activity peaks (and future audio volume peaks) from streaming video archives and extract clip highlights.

## Features & Architecture

To support future enhancements (such as AI-driven video metadata/audio analysis and advanced filtering), this project is built on a clean pipeline structure. Each phase is separated into distinct, modular components.

```
[Chat Log/Video Archive] 
           │
           ▼
 1. Data Input (reader.py)  ── Normalizes and parses CSV/JSON chat logs.
           │
           ▼
 2. Peak Analysis (analyzer.py) ── Identifies peak highlight moments using a sliding window.
           │
           ▼
 3. Video Editing (video.py) ── Spawns ffmpeg to clip the video precisely.
```

## Requirements

- Python 3.8+
- **ffmpeg** command-line tool
  - `ffmpeg` must be installed on your system and added to your system's `PATH` environment variable for video clipping functionality.

## Installation

Run the following command in the root directory of this repository to install the package in development mode:

```bash
pip install -e .
```

This will install the necessary dependencies (`click`, `pandas`, `numpy`) and register the `stream-clipper` command globally on your system/virtual environment.

## Usage

The basic command structure is as follows:

```bash
stream-clipper clip [VIDEO_PATH] [LOG_PATH] [OPTIONS]
```

### Examples

```bash
# Basic run with default parameters (outputs clips to ./output)
stream-clipper clip stream_archive.mp4 chat_log.csv

# Run with custom parameters: 10s window, 3x threshold, offset 5s before the peak, clipping for 10s
stream-clipper clip stream_archive.mp4 chat_log.json --window 10 --threshold 3.0 --offset 5 --duration 10 --output-dir custom_clips/
```

### Command Options

| Option | Default Value | Description |
| :--- | :--- | :--- |
| `--window` | `30.0` | Time window (seconds) to measure chat density. |
| `--threshold` | `2.0` | The multiplier of the overall mean chat density to detect a peak. |
| `--duration` | `15.0` | The duration of the output clip (seconds). |
| `--offset` | `10.0` | How many seconds before the peak timestamp the clip should start. |
| `--output-dir` | `output` | Directory where the generated video clips will be saved. |
| `--fast` | None (Flag) | Enables fast stream-copy clipping (`-c copy`). This matches keyframes and is extremely fast, but starting/ending positions may be slightly imprecise. |

---

## Development & Testing

### Generating Mock Assets

Before running tests or checking CLI functionality, generate a 60-second dummy video (with color bars and tone audio) and mock chat logs (with simulated spikes between 30 and 45 seconds):

```bash
python tests/generate_test_assets.py
```

### Running Unit Tests

Run the following command to execute the test suite:

```bash
python -m unittest tests/test_pipeline.py
```
