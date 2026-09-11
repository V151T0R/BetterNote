<div align="center">
  <img src="resources/icons/app_icon.png" width="128" height="128" alt="BetterNote Icon" />
  <h1>BetterNote</h1>
  <p>A minimal, distraction-free handwritten digital notebook for Windows & Linux.</p>


  <p>
    <a href="https://github.com/V151T0R/BetterNote/releases/tag/v1.0.0"><img src="https://img.shields.io/badge/release-v1.0.0-4F46E5?style=flat-square" alt="Release v1.0.0" /></a>
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-blue?style=flat-square" alt="Platform: Windows | Linux" />
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+" />
    <img src="https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-41CD52?style=flat-square&logo=qt&logoColor=white" alt="PySide6 / Qt" />
    <img src="https://img.shields.io/badge/license-MIT-gray?style=flat-square" alt="License: MIT" />
  </p>
</div>

---


## Highlights

- **Natural Inking**: Smooth, pressure-sensitive vector pen & blended highlighter.
- **Essential Tools**: Pen, Highlighter, Eraser, and a Lasso Selection tool to move strokes.
- **Distraction-Free**: Floating frosted toolbars, calming desk background, and clean paper.
- **Your Notes, Yours**: Saves directly to lightweight `.json` files. No accounts, no clouds, 100% offline.
- **Exports**: Quick export to PDF or images (`.png`, `.jpg`) when you need to share.

---

## Preview

<div align="center">
  <img src="resources/App_Preview/1.jpg.png" alt="BetterNote Workspace" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
  <p><em>Clean Workspace & Layout</em></p>
  
  <br/>
  
  <img src="resources/App_Preview/2.jpg.png" alt="BetterNote Inking & Sketches" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
  <p><em>Freehand Inking & Dark Mode</em></p>
</div>

---

## Getting Started

### Option 1: Standalone Executable
Download **`BetterNote.exe`** from [Releases](https://github.com/V151T0R/BetterNote/releases/tag/v1.0.0) (or run `dist/BetterNote.exe`) and double-click to launch. No installation or Python required.

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/V151T0R/BetterNote.git
cd BetterNote

# Install dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

### Build Executable
- **Windows**: Double-click **`build.bat`** (or run `pyinstaller BetterNote.spec --noconfirm`).
- **Linux**: Run `./build_linux.sh` to package a binary and desktop launcher.

---

## Shortcuts

| Action | Shortcut |
| :--- | :--- |
| Pen Tool | <kbd>P</kbd> |
| Highlighter Tool | <kbd>H</kbd> |
| Eraser Tool | <kbd>E</kbd> |
| Lasso Selection Tool | <kbd>S</kbd> |
| Undo / Redo | <kbd>Ctrl</kbd> + <kbd>Z</kbd> / <kbd>Ctrl</kbd> + <kbd>Y</kbd> |
| Save / Open | <kbd>Ctrl</kbd> + <kbd>S</kbd> / <kbd>Ctrl</kbd> + <kbd>O</kbd> |
| Pan Canvas | <kbd>Space</kbd> + Drag |
| Zoom In / Out | <kbd>Ctrl</kbd> + <kbd>+</kbd> / <kbd>Ctrl</kbd> + <kbd>-</kbd> |
| Reset Zoom | <kbd>Ctrl</kbd> + <kbd>0</kbd> |
| Fullscreen | <kbd>F11</kbd> |

---

## Built With

- [![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
- [![PySide6 / Qt](https://img.shields.io/badge/PySide6%20(Qt6)-41CD52?style=flat-square&logo=qt&logoColor=white)](https://wiki.qt.io/Qt_for_Python)
- [![PyInstaller](https://img.shields.io/badge/PyInstaller-2E3440?style=flat-square&logo=python&logoColor=white)](https://pyinstaller.org/)

---

<div align="center">
  <sub>Made for peaceful scribbling and sketching. Open source under the MIT License.</sub>
</div>
