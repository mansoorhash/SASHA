# SASHA

SASHA is a Windows desktop application being developed into a self-learning face recognition system. It uses PySide6 for the interface and OpenCV with DirectShow to discover and open cameras.

## Project goal

The planned system will detect the user's face in a camera feed and capture snapshots while it remains visible. The target capture interval is about five seconds initially, with the option to reduce it to one second as the model and performance improve.

When the face is no longer detected, SASHA will take a short burst of snapshots and compare them with previously confirmed images of the user. The goal is to identify useful views of different facial regions, including angled and side-profile views where the person is not looking directly at the camera. Confirmed matches can then be used to refine the model so it recognizes the user from more viewpoints over time. This repeated capture, comparison, and training cycle is the intended "self-learning" behavior.

This is the intended behavior, not a description of the current implementation. Face detection, snapshot capture, comparison, model training, and the face-loss response still need to be built.

## Current features

- Detect available DirectShow cameras and select one from the Settings panel.
- Display the selected camera's live feed.
- Show a Scan/Stop control and scanning status in the interface.
- Write runtime logs to the console and `logs/`.

The scanning control currently changes only the interface state. Face detection or recognition is not implemented yet.

## Requirements

- Windows with a working webcam or other DirectShow camera
- Python 3.12 (the version used for this project)
- Camera access enabled in Windows privacy settings

## Run locally

In PowerShell, from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Select a camera under **Settings > Camera** to start the preview. Close the window to stop the camera and exit.

If PowerShell blocks activation, you can use `.\.venv\Scripts\python.exe` in place of `python` for the install and run commands.

## Project layout

```text
app.py                 Application entry point
requirements.txt       Pinned Python dependencies
src/drivers/camera.py  DirectShow camera discovery and capture
src/ui/                PySide6 interface and settings
src/utils/logger.py    Console and file logging
```

Runtime logs and the local virtual environment are excluded from Git by `.gitignore`.

## License

SASHA is released under the [MIT License](LICENSE).
