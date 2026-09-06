# HandNote

A desktop handwritten note-taking application built with **Python and PySide6**, designed around a modular drawing engine with AI-powered handwriting, gesture, and shape recognition.

The goal of HandNote is to provide a modern digital notebook experience while keeping the application architecture extensible enough to support intelligent features later.

---

## Features

### Core Note-Taking

* Handwritten notes
* Pen and highlighter
* Eraser
* Undo / redo
* Multiple pages
* Multiple notebooks
* Page navigation
* Zoom and pan
* Different page backgrounds

  * Blank
  * Ruled
  * Grid
  * Dotted

### Drawing

* Smooth freehand strokes
* Adjustable pen size
* Adjustable pen color
* Stylus support
* Pressure-sensitive strokes
* Stroke-based document representation

### AI Features

* Handwriting recognition
* Gesture recognition
* Shape recognition
* Intelligent shape correction
* AI-assisted note processing
* Future AI-powered search and summarization

---

# Architecture

HandNote follows a modular architecture where the UI, drawing engine, document model, storage system, and AI systems are separated.

```text
                         HandNote
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
         UI              Core Editor           AI
          │                 │                 │
     ┌────┼────┐       ┌────┼────┐       ┌────┼────┐
     │    │    │       │    │    │       │    │    │
 Toolbar Sidebar Canvas  Page Stroke Tools Gesture Shape OCR
                                      │
                                      ▼
                                  Document
                                      │
                                      ▼
                                   Storage
```

The main principle is:

> The UI should display and interact with the document, but it should not own the document's data or business logic.

---

# Project Structure

```text
HandNote/
│
├── main.py
│
├── app/
│   ├── __init__.py
│   ├── application.py
│   └── config.py
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── toolbar.py
│   ├── sidebar.py
│   └── canvas_widget.py
│
├── core/
│   ├── __init__.py
│   ├── document.py
│   ├── notebook.py
│   ├── page.py
│   ├── stroke.py
│   ├── drawing_engine.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── pen.py
│   │   ├── eraser.py
│   │   ├── highlighter.py
│   │   └── selection.py
│   │
│   └── commands/
│       ├── __init__.py
│       ├── add_stroke.py
│       ├── delete_stroke.py
│       ├── move_stroke.py
│       └── command_manager.py
│
├── ai/
│   ├── __init__.py
│   ├── ai_manager.py
│   │
│   ├── gesture/
│   │   ├── __init__.py
│   │   ├── recognizer.py
│   │   ├── features.py
│   │   └── gestures.py
│   │
│   ├── handwriting/
│   │   ├── __init__.py
│   │   ├── recognizer.py
│   │   └── processor.py
│   │
│   ├── shapes/
│   │   ├── __init__.py
│   │   └── recognizer.py
│   │
│   └── assistant/
│       ├── __init__.py
│       └── assistant.py
│
├── storage/
│   ├── __init__.py
│   ├── document_store.py
│   └── json_store.py
│
├── resources/
│   ├── icons/
│   ├── themes/
│   └── models/
│
├── tests/
│   ├── test_stroke.py
│   ├── test_drawing.py
│   ├── test_document.py
│   ├── test_storage.py
│   └── test_ai.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

