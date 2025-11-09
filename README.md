# Select Screen Zone

Select Screen Zone is a cross-platform desktop prototype that lets you draw a rectangle on the screen, capture the underlying pixels, and automatically suggest UI elements detected inside the selected region. The project combines image-based OCR and (optionally) Windows UI Automation metadata to surface candidate controls such as buttons, folders, menu items, and other labels.

## Features

- 🔲 Full-screen translucent overlay for drawing a selection rectangle.
- 🖼️ High-fidelity screen capture powered by [`mss`](https://github.com/BoboTiG/python-mss).
- 🧠 Text recognition via [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) using the `pytesseract` Python bindings.
- ♿ Optional Windows-only accessibility integration backed by `uiautomation` for precise control metadata.
- 📋 Copy suggestions directly from the UI for reuse in automations or scripts.

## Getting started

1. **Install system dependencies**

   - Ensure that Python 3.10+ is available on your system.
   - Install [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html) and make sure the `tesseract` binary is on your `PATH`.
   - (Windows only) Install the [UIAutomation for Python](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows) prerequisites.

2. **Install Python packages**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**

   ```bash
   python main.py
   ```

   Click **Select Screen Zone** and drag a rectangle across any region of your desktop. Once you release the mouse button the application captures the pixels and populates suggestions.

## Optional configuration

- On Windows, installing `uiautomation` enables rich metadata (control type, automation id, process id). Without it the app gracefully falls back to OCR-only suggestions.
- You can change the OCR confidence threshold or combine multiple detectors by editing the modules under `src/selectscreenzone/analyzers/`.

## Project structure

```
.
├── main.py
├── README.md
├── requirements.txt
└── src/
    └── selectscreenzone/
        ├── analyzers/
        │   ├── __init__.py
        │   ├── accessibility.py
        │   └── ocr.py
        ├── __init__.py
        ├── app.py
        ├── screenshot.py
        ├── selection_overlay.py
        └── suggestions.py
```

## Roadmap

- Improve the accessibility traversal to query only elements intersecting the selected rectangle.
- Add model-driven UI detection for non-textual controls (icons, toggle buttons, etc.).
- Record historical suggestions and allow exporting to JSON.

Contributions and feedback are welcome!
