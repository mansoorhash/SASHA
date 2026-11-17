# SASHA

SASHA is a Windows desktop application for live camera preview and face recognition. It uses PySide6 for the interface, OpenCV with DirectShow for camera access, DeepFace's FaceNet model for face embeddings, and SciPy to assign each known name to at most one face per processed frame.

## Current features

- Discover and select a DirectShow camera, then display its live feed even when scanning is off.
- Start and stop face scanning in a worker thread so the interface stays responsive.
- Detect faces, ignore detections smaller than the configured minimum, and discard smaller boxes contained inside larger detections.
- Compare normalized face embeddings with saved profiles using cosine distance. Faces that do not meet the matching threshold remain unknown.
- Assign each enrolled name to at most one detected face per processed frame. Show recognized names and boxes on the camera feed.
- Add embeddings for recognized people at the configured interval and save face memory when the scan worker stops.
- Write application logs to the console and `logs/`.

SASHA expands its collection of embeddings for known people. It does not retrain the FaceNet model or automatically create a profile for an unknown person. Automatic additions currently use the recognition result; they do not have a separate verification step. Recognition accuracy has not yet been measured on a labeled test set.

## Requirements

- Windows with Python 3.12 and a DirectShow-compatible camera
- Camera access enabled in Windows privacy settings

## Run locally

From the project directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` instead of `python` for the install and run commands.

To enroll a person, put a JPG or PNG image containing exactly one face in `reference_images/`, with the person's name as the filename, such as `Alice.jpg`. The application creates this directory if it does not exist. Reference images are read when face memory is initialized at startup. An existing saved profile takes precedence over a reference image with the same name.

In the application, select a camera under **Settings > Camera**. The preview starts immediately. Press **Scan** to begin recognition and **Stop** to end the scan and save face memory. Closing the application also stops an active scan and saves its memory.

The current configuration uses FaceNet with the OpenCV detector and a cosine distance threshold of `0.40`. Other scan settings are in `src/config.py`.

## Project layout

```text
app.py                    Application entry point
requirements.txt          Pinned direct dependencies
src/config.py             Recognition and learning settings
src/drivers/camera.py     Camera discovery and capture
src/scanning/worker.py    Detection, matching, and learning worker
src/scanning/memory.py    Reference profiles and saved embeddings
src/ui/                   PySide6 interface and settings
src/utils/logger.py       Console and file logging
```

`reference_images/`, `face_memory.pkl`, the local virtual environment, and runtime logs are excluded from Git. Keep reference images and saved face memory private.

## License

SASHA is released under the [MIT License](LICENSE).
