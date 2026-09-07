# 📓 BetterNote

A modern, distraction-free handwritten digital notebook application built with **Python** and **PySide6 (Qt)**. Designed with a modular vector inking engine, undo/redo command history, customizable color palettes, multi-page notebooks, and export capabilities.

![BetterNote Banner](resources/icons/app_icon.svg)

---

## ✨ Features

### ✍️ Vector Inking & Tools
- **Pressure-Sensitive Drawing**: Smooth freehand strokes rendered using quadratic Bézier curve interpolation.
- **Pen Tool (`P`)**: Clean vector pen with dynamic width and color.
- **Highlighter Tool (`H`)**: Translucent, blended highlighting for annotating notes and sketches.
- **Eraser Tool (`E`)**: Precise stroke-intersection eraser with scalable deletion radius.
- **Selection & Transform Tool (`S`)**: Lasso/bounding-box tool to select individual or groups of strokes and drag/reposition them across the canvas.
- **Interactive Thickness Slider**: Floating vertical slider for adjusting stroke widths on the fly.

### 🎨 Color & Swatch Management
- **Smart Color Swap Button**: Instant access to custom color pickers.
- **Pinned Swatches**: Quick-select color bar with right-click-to-unpin support.
- **Custom Color Palette**: Curated soothing default colors matching the app's signature indigo theme (Charcoal, Royal Indigo, Ocean Blue, Ribbon Rose, Warm Amber, Emerald).
- **Custom Page Backgrounds**: Change notebook page background colors per document.

### 📑 Document & Page Handling
- **Multi-Page Documents**: Create, navigate, clear, and delete pages seamlessly.
- **Page Indicator**: Clean `Current / Total` page counter with instant navigation buttons.
- **Zoom & Pan**:
  - Smooth zoom controls from `25%` to `400%`.
  - Pan freely across large canvases using **`Space` + Mouse Drag** or middle-mouse click.
- **Robust Command History**: Complete multi-step **Undo (`Ctrl+Z`)** and **Redo (`Ctrl+Y`)** powered by the Command Pattern.

### 💾 File Formats & Export
- **Native JSON Notebooks (`.json`)**: Lightweight, human-readable document format storing exact stroke vectors, widths, colors, and metadata.
- **Export to PDF**: Vector export creating print-ready document pages.
- **Export to Image**: High-resolution raster export supporting `.png`, `.jpg`, and `.bmp`.

### 🖥️ Modern UI & Styling
- **Calm, Soothing Workspace**: Soft slate desk background with realistic paper sheet elevation and drop-shadows.
- **Floating Frosted Toolbars**: Pill-shaped toolbars for tools, page controls, stroke thickness, and zoom.
- **Dual-State Icons**: High-contrast icons that switch between crisp white on active Indigo badges and subtle slate graphite when inactive.
- **Distraction-Free Fullscreen (`F11`)**: One-click fullscreen mode for focused writing and tablet sketching.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| **`P`** | Activate Pen tool |
| **`H`** | Activate Highlighter tool |
| **`E`** | Activate Eraser tool |
| **`S`** | Activate Selection tool |
| **`Ctrl + Z`** | Undo last action |
| **`Ctrl + Y`** / **`Ctrl + Shift + Z`** | Redo action |
| **`Ctrl + S`** | Save document |
| **`Ctrl + Shift + S`** | Save document as… |
| **`Ctrl + O`** | Open existing document |
| **`Ctrl + +`** | Zoom in |
| **`Ctrl + -`** | Zoom out |
| **`Ctrl + 0`** | Reset zoom to 100% |
| **`Space + Drag`** | Pan canvas |
| **`F11`** | Toggle Fullscreen |

---

## 🏛️ Architecture Overview

BetterNote follows a strict modular architecture separating UI presentation, editing logic, document representation, and file storage:

```text
                        BetterNote
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
         UI            Core Editor         Storage
          │                 │                 │
     ┌────┼────┐       ┌────┼────┐            ▼
     │    │    │       │    │    │        JSON Store
  Toolbar Canvas  Page Stroke Tools    (Save / Load)
  Widgets Overlays     │        │
                       ▼        ▼
                   Notebook  Commands
                              (Undo/Redo)
```

- **`core/`**: Document data models (`Notebook`, `Page`, `Stroke`), vector tools, and undo/redo command definitions.
- **`ui/`**: Qt widgets, drawing canvas (`CanvasWidget`), floating toolbars, and main application window.
- **`app/`**: Application lifecycle, theme stylesheet generator, and global configuration.
- **`storage/`**: Serialization engine for reading and writing `.json` notebooks and exporting documents.
- **`resources/`**: High-resolution SVG vectors and multi-resolution Windows icons (`.ico`).

---

## 📁 Project Structure

```text
BetterNote/
├── main.py                     # Application entry point
├── requirements.txt            # Python package dependencies
├── README.md                   # Project documentation
│
├── app/
│   ├── __init__.py
│   ├── application.py          # QApplication setup & theme stylesheet builder
│   └── config.py               # Constants, zoom steps, and default palettes
│
├── core/
│   ├── notebook.py             # Notebook model containing pages
│   ├── page.py                 # Page model containing strokes & background
│   ├── stroke.py               # Stroke point coordinates & properties
│   ├── drawing_engine.py       # Core tool coordinator and event router
│   ├── commands/               # Command pattern implementations (Undo/Redo)
│   │   ├── command_manager.py
│   │   ├── add_stroke.py
│   │   ├── delete_stroke.py
│   │   └── move_stroke.py
│   └── tools/                  # Drawing tools
│       ├── tool.py             # Base tool class
│       ├── pen.py
│       ├── highlighter.py
│       ├── eraser.py
│       └── selection.py
│
├── ui/
│   ├── main_window.py          # Main application window & menus
│   ├── canvas_widget.py        # Vector canvas drawing surface
│   └── toolbar.py              # Floating toolbar, slider, & color swatches
│
├── storage/
│   ├── document_store.py       # Abstract document store interface
│   └── json_store.py           # Native JSON serialization
│
└── resources/
    └── icons/
        ├── app_icon.svg        # Scalable vector application icon
        ├── app_icon.ico        # Multi-size Windows executable icon
        └── *.svg               # Toolbar tool icons (pen, eraser, etc.)
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+** installed on your system.
- Windows 10/11 recommended for full stylus and pressure sensitivity support.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/BetterNote.git
   cd BetterNote
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Launch BetterNote:**
   ```powershell
   python main.py
   ```

---

## 📦 Building Executables & Installers

### 1. Build Standalone `.exe` (PyInstaller)
You can compile BetterNote into a standalone single-file Windows executable:

- **Option A (Easiest)**: Double-click **`build.bat`** in the project folder.
- **Option B (Terminal)**:
  ```powershell
  pyinstaller BetterNote.spec --noconfirm
  ```

The compiled binary will be placed at:
> **`dist\BetterNote.exe`**

---

### 2. Build Windows Installer (`.msi` via WiX Toolset)
To generate an enterprise-grade Windows Installer (`.msi`) that installs to `Program Files` and creates Start Menu and Desktop shortcuts:

1. Install the WiX CLI (if not already installed):
   ```powershell
   winget install WiXToolset.WiXCLI
   ```
2. Compile the installer:
   ```powershell
   wix build BetterNote.wxs -o dist\BetterNote.msi
   ```
Output:
> **`dist\BetterNote.msi`**

---

### 3. Build Setup Wizard (`BetterNote_Setup.exe` via Inno Setup)
To generate a standard graphical setup installer wizard:

1. Install Inno Setup:
   ```powershell
   winget install JR.InnoSetup
   ```
2. Compile the script:
   ```powershell
   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" BetterNote.iss
   ```
Output:
> **`dist\BetterNote_Setup.exe`**

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
