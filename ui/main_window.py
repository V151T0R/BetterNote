import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QFileDialog, QColorDialog, QLabel, QMessageBox,
                               QFrame, QToolButton, QMenu, QWidgetAction,
                               QGraphicsDropShadowEffect, QScrollArea, QApplication)
from PySide6.QtGui import QColor, QKeySequence, QAction, QIcon, QPixmap, QPalette
from PySide6.QtCore import Qt, QEvent, QSize, QByteArray

from core.drawing_engine import DrawingEngine
from core.notebook import Notebook
from core.commands.command_manager import CommandManager
from core.tools.pen import Pen
from core.tools.eraser import Eraser
from core.tools.highlighter import Highlighter

from ui.canvas_widget import CanvasWidget
from ui.toolbar import _WrapLayout, ColorSwatchButton
from storage.json_store import JSONStore
from app.config import DEFAULT_PINNED_COLORS

def get_colored_icon(svg_path: str, color_hex: str) -> QIcon:
    if not os.path.exists(svg_path):
        return QIcon()
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    svg_content = svg_content.replace('currentColor', color_hex)
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray(svg_content.encode('utf-8')))
    return QIcon(pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GoodNote")
        self.resize(1100, 800)
        self.setMinimumSize(480, 360)
        
        icon_path = r"C:\Users\sourav\.gemini\antigravity\brain\86f29009-f33b-4a8b-90f0-f2ba532339c7\goodnote_icon_1788717414791.jpg"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.notebook = Notebook()
        self.command_manager = CommandManager()
        self.engine = DrawingEngine(self.notebook, self.command_manager)
        
        self.engine.set_tool("pen", Pen())
        self.engine.set_tool("eraser", Eraser())
        self.engine.set_tool("highlighter", Highlighter())
        self.engine.use_tool("pen")

        self.canvas = CanvasWidget(self.engine)
        
        self.pinned_colors = list(DEFAULT_PINNED_COLORS)
        self.current_file = None

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.setCentralWidget(self.scroll_area)

        self.apply_theme()

        self._build_file_menu_actions()
        self._build_colors_menu()
        self._build_pages_menu()
        self._build_floating_toolbar()
        self._build_thickness_bar()
        self._build_zoom_bar()
        self._build_shortcuts()
        
        self._update_icon_colors()

        self.update_page_label()
        self.update_zoom_label()
        self.position_overlays()

    def _build_floating_toolbar(self):
        self.toolbar = QWidget(self.scroll_area.viewport())
        self.toolbar.setObjectName("floatingToolbar")
        self.toolbar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect(self.toolbar)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.toolbar.setGraphicsEffect(shadow)

        row = QHBoxLayout(self.toolbar)
        row.setContentsMargins(10, 6, 10, 6)
        row.setSpacing(6)

        self.file_menu_button = QToolButton()
        self.file_menu_button.setObjectName("fileMenuButton")
        self.file_menu_button.setText("File")
        self.file_menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.file_menu_button.setMenu(self._file_menu)

        self.icon_size = QSize(20, 20)

        self.btn_pen = QPushButton()
        self.btn_pen.setIconSize(self.icon_size)
        self.btn_pen.setToolTip("Pen (P)")
        self.btn_pen.setCheckable(True)
        self.btn_pen.setChecked(True)
        self.btn_pen.clicked.connect(self.activate_pen)

        self.btn_highlighter = QPushButton()
        self.btn_highlighter.setIconSize(self.icon_size)
        self.btn_highlighter.setToolTip("Highlighter (H)")
        self.btn_highlighter.setCheckable(True)
        self.btn_highlighter.clicked.connect(self.activate_highlighter)

        self.btn_eraser = QPushButton()
        self.btn_eraser.setIconSize(self.icon_size)
        self.btn_eraser.setToolTip("Eraser (E)")
        self.btn_eraser.setCheckable(True)
        self.btn_eraser.clicked.connect(self.activate_eraser)

        self.btn_select = QPushButton()
        self.btn_select.setIconSize(self.icon_size)
        self.btn_select.setToolTip("Select (S)")
        self.btn_select.setCheckable(True)
        self.btn_select.clicked.connect(self.activate_select)

        self.colors_button = QToolButton()
        self.colors_button.setObjectName("colorButton")
        self.colors_button.setToolTip("Colors")
        self.colors_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.colors_button.setMenu(self._colors_menu)
        self._recolor_colors_button()

        for b in (self.btn_pen, self.btn_highlighter, self.btn_eraser, self.btn_select):
            b.setObjectName("iconButton")
            b.setFixedSize(36, 36)
        
        self.colors_button.setFixedSize(26, 26) 

        self.btn_prev = QPushButton()
        self.btn_prev.setIconSize(self.icon_size)
        self.btn_prev.setObjectName("navButton")
        self.btn_prev.setFixedSize(30, 36)
        self.btn_prev.setToolTip("Previous page")
        self.btn_prev.clicked.connect(self.prev_page)

        self.page_label = QLabel()
        self.page_label.setObjectName("pageLabel")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setMinimumWidth(56)

        self.btn_next = QPushButton()
        self.btn_next.setIconSize(self.icon_size)
        self.btn_next.setObjectName("navButton")
        self.btn_next.setFixedSize(30, 36)
        self.btn_next.setToolTip("Next page")
        self.btn_next.clicked.connect(self.next_page)

        self.btn_add_page = QPushButton()
        self.btn_add_page.setIconSize(self.icon_size)
        self.btn_add_page.setObjectName("iconButton")
        self.btn_add_page.setToolTip("Add page")
        self.btn_add_page.setFixedSize(36, 36)
        self.btn_add_page.clicked.connect(self.add_page)

        self.pages_button = QToolButton()
        self.pages_button.setIconSize(self.icon_size)
        self.pages_button.setObjectName("iconButton")
        self.pages_button.setToolTip("More page options")
        self.pages_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.pages_button.setMenu(self._pages_menu)
        self.pages_button.setFixedSize(36, 36)
        
        self.btn_fullscreen = QPushButton()
        self.btn_fullscreen.setIconSize(self.icon_size)
        self.btn_fullscreen.setObjectName("iconButton")
        self.btn_fullscreen.setToolTip("Toggle Fullscreen")
        self.btn_fullscreen.setFixedSize(36, 36)
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)

        row.addWidget(self.file_menu_button)
        row.addWidget(self._vline())
        row.addWidget(self.btn_select)
        row.addWidget(self.btn_pen)
        row.addWidget(self.btn_highlighter)
        row.addWidget(self.btn_eraser)
        row.addSpacing(4)
        row.addWidget(self.colors_button)
        row.addSpacing(4)
        row.addWidget(self._vline())
        row.addWidget(self.btn_prev)
        row.addWidget(self.page_label)
        row.addWidget(self.btn_next)
        row.addWidget(self.btn_add_page)
        row.addWidget(self.pages_button)
        row.addWidget(self._vline())
        row.addWidget(self.btn_fullscreen)
        self.toolbar.adjustSize()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
        self._update_icon_colors()

    def _build_thickness_bar(self):
        self.thickness_bar = QWidget(self.scroll_area.viewport())
        self.thickness_bar.setObjectName("floatingToolbar") # reuse floating panel styling
        self.thickness_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect(self.thickness_bar)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.thickness_bar.setGraphicsEffect(shadow)

        col = QVBoxLayout(self.thickness_bar)
        col.setContentsMargins(6, 10, 6, 10)
        col.setSpacing(12)

        self.thickness_btns = []
        sizes = [
            (3.0, 6),
            (6.0, 10),
            (12.0, 16),
            (20.0, 22)
        ]
        
        for width_val, dot_size in sizes:
            btn = QPushButton()
            btn.setObjectName("thicknessButton")
            btn.setFixedSize(32, 32)
            btn.setCheckable(True)
            btn.setProperty("stroke_width", width_val)
            
            # The circle is drawn via stylesheet based on dot_size
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                }}
                QPushButton::indicator {{
                    width: 0px; height: 0px; /* Disable default */
                }}
            """)
            
            # Create an inner widget for the actual dot to ensure perfectly round
            dot = QWidget(btn)
            dot.setFixedSize(dot_size, dot_size)
            dot.setObjectName("thicknessDot")
            # center it
            dot.move((32 - dot_size) // 2, (32 - dot_size) // 2)
            
            btn.clicked.connect(lambda checked, b=btn: self.apply_thickness(b))
            self.thickness_btns.append(btn)
            col.addWidget(btn)
            
        self.thickness_btns[0].setChecked(True)
        self.thickness_bar.adjustSize()

    def apply_thickness(self, btn):
        for b in self.thickness_btns:
            b.setChecked(b == btn)
        width = btn.property("stroke_width")
        
        if hasattr(self.engine.tools["pen"], "width"):
            self.engine.tools["pen"].width = width
        # Highlighter thickness is usually larger, scale it slightly
        if hasattr(self.engine.tools["highlighter"], "width"):
            self.engine.tools["highlighter"].width = width * 2.0
            
    def _recolor_thickness_bar(self):
        # We need to style the inner dots
        text_color = self.palette().color(QPalette.ColorRole.WindowText).name()
        accent = self.palette().color(QPalette.ColorRole.Highlight).name()
        
        for btn in self.thickness_btns:
            dot = btn.findChild(QWidget, "thicknessDot")
            if dot:
                # If button is checked, use accent color, else text_color
                color = accent if btn.isChecked() else text_color
                r = dot.width() // 2
                dot.setStyleSheet(f"""
                    QWidget#thicknessDot {{
                        background-color: {color};
                        border-radius: {r}px;
                    }}
                """)

    def _update_icon_colors(self):
        text_color = self.palette().color(QPalette.ColorRole.WindowText).name()
        
        self.btn_select.setIcon(get_colored_icon("resources/icons/select.svg", text_color))
        self.btn_pen.setIcon(get_colored_icon("resources/icons/pen.svg", text_color))
        self.btn_highlighter.setIcon(get_colored_icon("resources/icons/highlighter.svg", text_color))
        self.btn_eraser.setIcon(get_colored_icon("resources/icons/eraser.svg", text_color))
        self.btn_prev.setIcon(get_colored_icon("resources/icons/prev.svg", text_color))
        self.btn_next.setIcon(get_colored_icon("resources/icons/next.svg", text_color))
        self.btn_add_page.setIcon(get_colored_icon("resources/icons/add.svg", text_color))
        self.pages_button.setIcon(get_colored_icon("resources/icons/more.svg", text_color))
        
        if self.isFullScreen():
            self.btn_fullscreen.setIcon(get_colored_icon("resources/icons/fullscreen_exit.svg", text_color))
        else:
            self.btn_fullscreen.setIcon(get_colored_icon("resources/icons/fullscreen.svg", text_color))
            
        self._recolor_thickness_bar()

    def _build_zoom_bar(self):
        self.zoom_bar = QWidget(self.scroll_area.viewport())
        self.zoom_bar.setObjectName("zoomBar")
        self.zoom_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect(self.zoom_bar)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.zoom_bar.setGraphicsEffect(shadow)

        row = QHBoxLayout(self.zoom_bar)
        row.setContentsMargins(8, 5, 8, 5)
        row.setSpacing(4)

        btn_out = QPushButton("−")
        btn_out.setObjectName("zoomButton")
        btn_out.setFixedSize(28, 28)
        btn_out.setToolTip("Zoom out (Ctrl+−)")
        btn_out.clicked.connect(self.canvas.zoom_out)
        btn_out.clicked.connect(self.update_zoom_label)

        self.zoom_label = QLabel()
        self.zoom_label.setObjectName("zoomLabel")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_label.mousePressEvent = lambda e: self._reset_zoom_clicked()

        btn_in = QPushButton("+")
        btn_in.setObjectName("zoomButton")
        btn_in.setFixedSize(28, 28)
        btn_in.setToolTip("Zoom in (Ctrl++)")
        btn_in.clicked.connect(self.canvas.zoom_in)
        btn_in.clicked.connect(self.update_zoom_label)

        row.addWidget(btn_out)
        row.addWidget(self.zoom_label)
        row.addWidget(btn_in)
        self.zoom_bar.adjustSize()

    def _reset_zoom_clicked(self):
        self.canvas.zoom_reset()
        self.update_zoom_label()

    def update_zoom_label(self):
        self.zoom_label.setText(f"{round(self.canvas.zoom * 100)}%")

    def _build_shortcuts(self):
        act_zoom_in = QAction(self)
        act_zoom_in.setShortcuts([QKeySequence.StandardKey.ZoomIn, QKeySequence("Ctrl+=")])
        act_zoom_in.triggered.connect(lambda: (self.canvas.zoom_in(), self.update_zoom_label()))
        self.addAction(act_zoom_in)

        act_zoom_out = QAction(self)
        act_zoom_out.setShortcuts([QKeySequence.StandardKey.ZoomOut])
        act_zoom_out.triggered.connect(lambda: (self.canvas.zoom_out(), self.update_zoom_label()))
        self.addAction(act_zoom_out)

        act_zoom_reset = QAction(self)
        act_zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        act_zoom_reset.triggered.connect(self._reset_zoom_clicked)
        self.addAction(act_zoom_reset)

        act_select = QAction(self)
        act_select.setShortcut(QKeySequence("S"))
        act_select.triggered.connect(self.activate_select)
        self.addAction(act_select)

        act_pen = QAction(self)
        act_pen.setShortcut(QKeySequence("P"))
        act_pen.triggered.connect(self.activate_pen)
        self.addAction(act_pen)
        
        act_highlighter = QAction(self)
        act_highlighter.setShortcut(QKeySequence("H"))
        act_highlighter.triggered.connect(self.activate_highlighter)
        self.addAction(act_highlighter)

        act_eraser = QAction(self)
        act_eraser.setShortcut(QKeySequence("E"))
        act_eraser.triggered.connect(self.activate_eraser)
        self.addAction(act_eraser)
        
        act_undo = QAction(self)
        act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        act_undo.triggered.connect(self.undo)
        self.addAction(act_undo)

        act_redo = QAction(self)
        act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        act_redo.triggered.connect(self.redo)
        self.addAction(act_redo)
        
    def undo(self):
        self.engine.undo()
        self.canvas.refresh_current_page()
        
    def redo(self):
        self.engine.redo()
        self.canvas.refresh_current_page()

    def position_overlays(self):
        viewport = self.scroll_area.viewport()
        
        self.toolbar.adjustSize()
        x = max(8, (viewport.width() - self.toolbar.width()) // 2)
        self.toolbar.move(x, 10)
        self.toolbar.raise_()

        self.zoom_bar.adjustSize()
        zx = max(8, viewport.width() - self.zoom_bar.width() - 14)
        zy = max(8, viewport.height() - self.zoom_bar.height() - 14)
        self.zoom_bar.move(zx, zy)
        self.zoom_bar.raise_()
        
        self.thickness_bar.adjustSize()
        ty = max(8, (viewport.height() - self.thickness_bar.height()) // 2)
        self.thickness_bar.move(14, ty)
        self.thickness_bar.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_overlays()

    def showEvent(self, event):
        super().showEvent(event)
        self.position_overlays()

    def apply_theme(self):
        if getattr(self, "_applying_theme", False):
            return
        self._applying_theme = True
        try:
            from app.application import build_theme_stylesheet
            base_pt = QApplication.font().pointSizeF()
            if base_pt <= 0:
                base_pt = 10.0
            self.setStyleSheet(build_theme_stylesheet(self.palette(), base_pt))
            if hasattr(self, "swatch_layout"):
                self.refresh_pinned_swatches()
            if hasattr(self, "colors_button"):
                self._recolor_colors_button()
            
            if hasattr(self, "btn_pen"):
                self._update_icon_colors()
        finally:
            self._applying_theme = False

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.ApplicationPaletteChange, QEvent.Type.FontChange):
            self.apply_theme()
            self.canvas.update()

    def _vline(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setObjectName("toolbarDivider")
        return line

    def _recolor_colors_button(self):
        tool = self.engine.active_tool
        color = getattr(tool, "color", "#000000")
        if len(color) == 9 and color.startswith("#"):
            color = color[:7]
            
        self.colors_button.setStyleSheet(f"""
            QToolButton#colorButton {{
                background-color: {color};
                border: 2px solid rgba(128, 128, 128, 100);
                border-radius: 13px;
                padding: 0px !important;
                margin: 0px !important;
            }}
            QToolButton#colorButton:hover {{
                border: 2px solid rgba(200, 200, 200, 200);
            }}
        """)

    def _build_file_menu_actions(self):
        menu = QMenu(self)
        act_open = QAction("Open…", self)
        act_open.setShortcut(QKeySequence.StandardKey.Open)
        act_open.triggered.connect(self.load_file)
        menu.addAction(act_open)

        act_save = QAction("Save", self)
        act_save.setShortcut(QKeySequence.StandardKey.Save)
        act_save.triggered.connect(self.save_file)
        menu.addAction(act_save)

        act_save_as = QAction("Save As…", self)
        act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        act_save_as.triggered.connect(self.save_file_as)
        menu.addAction(act_save_as)

        menu.addSeparator()

        act_export_pdf = QAction("Export as PDF…", self)
        act_export_pdf.triggered.connect(self.canvas.export_pdf)
        menu.addAction(act_export_pdf)

        act_export_image = QAction("Export as Image…", self)
        act_export_image.triggered.connect(self.canvas.export_image)
        menu.addAction(act_export_image)

        menu.addSeparator()

        act_background = QAction("Page Background…", self)
        act_background.triggered.connect(self.choose_background)
        menu.addAction(act_background)

        self._file_menu = menu
        self.addActions(menu.actions())

    def _build_colors_menu(self):
        menu = QMenu(self)
        swatch_widget = QWidget()
        self.swatch_layout = _WrapLayout(swatch_widget, h_spacing=6, v_spacing=6)
        swatch_widget.setMinimumWidth(190)

        swatch_action = QWidgetAction(menu)
        swatch_action.setDefaultWidget(swatch_widget)
        menu.addAction(swatch_action)
        menu.addSeparator()

        act_custom = QAction("Custom Color…", self)
        act_custom.triggered.connect(self.choose_color)
        menu.addAction(act_custom)

        act_pin = QAction("Pin Current Color", self)
        act_pin.triggered.connect(self.pin_current_color)
        menu.addAction(act_pin)

        self._colors_menu = menu
        self.refresh_pinned_swatches()

    def _build_pages_menu(self):
        menu = QMenu(self)
        act_delete = QAction("Delete Page", self)
        act_delete.triggered.connect(self.delete_page)
        menu.addAction(act_delete)

        menu.addSeparator()

        act_clear = QAction("Clear Page", self)
        act_clear.triggered.connect(self.canvas.clear_page)
        menu.addAction(act_clear)
        self._pages_menu = menu

    def activate_pen(self):
        self.engine.use_tool("pen")
        self.btn_pen.setChecked(True)
        self.btn_highlighter.setChecked(False)
        self.btn_eraser.setChecked(False)
        self.btn_select.setChecked(False)
        self._recolor_colors_button()
        
    def activate_highlighter(self):
        self.engine.use_tool("highlighter")
        self.btn_pen.setChecked(False)
        self.btn_highlighter.setChecked(True)
        self.btn_eraser.setChecked(False)
        self.btn_select.setChecked(False)
        self._recolor_colors_button()

    def activate_eraser(self):
        self.engine.use_tool("eraser")
        self.btn_pen.setChecked(False)
        self.btn_highlighter.setChecked(False)
        self.btn_eraser.setChecked(True)
        self.btn_select.setChecked(False)
    def activate_select(self):
        self.engine.use_tool("selection")
        self.btn_pen.setChecked(False)
        self.btn_highlighter.setChecked(False)
        self.btn_eraser.setChecked(False)
        self.btn_select.setChecked(True)
        self.canvas.update()


    def apply_color(self, hex_color):
        if hasattr(self.engine.tools["pen"], "color"):
            self.engine.tools["pen"].color = hex_color
        if hasattr(self.engine.tools["highlighter"], "color"):
            self.engine.tools["highlighter"].color = hex_color
            
        self._recolor_colors_button()
        if isinstance(self.engine.active_tool, Eraser):
            self.activate_pen()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.apply_color(color.name())

    def pin_current_color(self):
        tool = self.engine.active_tool
        color = getattr(tool, "color", "#000000")
        if len(color) == 9 and color.startswith("#"):
            color = color[:7]
        if color not in self.pinned_colors:
            self.pinned_colors.append(color)
            self.refresh_pinned_swatches()

    def unpin_color(self, hex_color):
        if hex_color in self.pinned_colors and len(self.pinned_colors) > 1:
            self.pinned_colors.remove(hex_color)
            self.refresh_pinned_swatches()

    def refresh_pinned_swatches(self):
        self.swatch_layout.clear()
        for hex_color in self.pinned_colors:
            swatch = ColorSwatchButton(hex_color, self.apply_color, removable_cb=self.unpin_color)
            self.swatch_layout.addWidget(swatch)

    def choose_background(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_page_background(color.name())

    def update_page_label(self):
        total = len(self.notebook.pages)
        current = self.engine.current_page_index + 1
        self.page_label.setText(f"{current} / {total}")

    def add_page(self):
        self.canvas.add_page()
        self.update_page_label()

    def delete_page(self):
        if len(self.notebook.pages) <= 1:
            QMessageBox.information(self, "Can't Delete", "A document needs at least one page.")
            return
        reply = QMessageBox.question(
            self, "Delete Page",
            "Delete the current page? This can't be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.delete_current_page()
            self.update_page_label()

    def prev_page(self):
        self.canvas.go_to_page(self.engine.current_page_index - 1)
        self.update_page_label()

    def next_page(self):
        self.canvas.go_to_page(self.engine.current_page_index + 1)
        self.update_page_label()

    def save_file(self):
        if self.current_file:
            JSONStore.save(self.notebook, self.current_file)
            self.canvas.dirty = False
            print(f"Saved {len(self.notebook.pages)} page(s) to {self.current_file}")
        else:
            self.save_file_as()

    def save_file_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Notes", "", "JSON Files (*.json)")
        if filename:
            JSONStore.save(self.notebook, filename)
            self.current_file = filename
            self.canvas.dirty = False
            print(f"Saved {len(self.notebook.pages)} page(s) to {filename}")

    def load_file(self):
        if not self.confirm_discard_if_dirty():
            return
        filename, _ = QFileDialog.getOpenFileName(self, "Load Notes", "", "JSON Files (*.json)")
        if filename:
            self.notebook = JSONStore.load(filename)
            self.engine.notebook = self.notebook
            self.engine.current_page_index = 0
            self.canvas.rebuild_all_paths()
            self.current_file = filename
            self.canvas.dirty = False
            self.update_page_label()
            print(f"Loaded {len(self.notebook.pages)} page(s) from {filename}")

    def confirm_discard_if_dirty(self):
        if not self.canvas.dirty:
            return True
        reply = QMessageBox.question(
            self, "Unsaved Changes",
            "You have unsaved changes. Do you want to save them first?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if reply == QMessageBox.StandardButton.Save:
            self.save_file()
            return not self.canvas.dirty
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def closeEvent(self, event):
        if self.confirm_discard_if_dirty():
            event.accept()
        else:
            event.ignore()
