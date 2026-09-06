import sys

with open('ui/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1 & 2. Add btn_select creation
old_btn_eraser = '''        self.btn_eraser = QPushButton()
        self.btn_eraser.setIconSize(self.icon_size)
        self.btn_eraser.setToolTip("Eraser (E)")
        self.btn_eraser.setCheckable(True)
        self.btn_eraser.clicked.connect(self.activate_eraser)'''
new_btn_eraser = old_btn_eraser + '''\n
        self.btn_select = QPushButton()
        self.btn_select.setIconSize(self.icon_size)
        self.btn_select.setToolTip("Select (S)")
        self.btn_select.setCheckable(True)
        self.btn_select.clicked.connect(self.activate_select)'''
content = content.replace(old_btn_eraser, new_btn_eraser)

# Add to group
old_group = '''for b in (self.btn_pen, self.btn_highlighter, self.btn_eraser):'''
new_group = '''for b in (self.btn_pen, self.btn_highlighter, self.btn_eraser, self.btn_select):'''
content = content.replace(old_group, new_group)

# Add to layout
old_layout = '''        row.addWidget(self.btn_pen)
        row.addWidget(self.btn_highlighter)
        row.addWidget(self.btn_eraser)'''
new_layout = '''        row.addWidget(self.btn_select)
        row.addWidget(self.btn_pen)
        row.addWidget(self.btn_highlighter)
        row.addWidget(self.btn_eraser)'''
content = content.replace(old_layout, new_layout)

# 3. Add to _update_icon_colors
old_icons = '''        self.btn_pen.setIcon(get_colored_icon("resources/icons/pen.svg", text_color))'''
new_icons = '''        self.btn_select.setIcon(get_colored_icon("resources/icons/select.svg", text_color))\n''' + old_icons
content = content.replace(old_icons, new_icons)

# 4. Add shortcut
old_shortcut = '''        act_pen = QAction(self)
        act_pen.setShortcut(QKeySequence("P"))
        act_pen.triggered.connect(self.activate_pen)
        self.addAction(act_pen)'''
new_shortcut = '''        act_select = QAction(self)
        act_select.setShortcut(QKeySequence("S"))
        act_select.triggered.connect(self.activate_select)
        self.addAction(act_select)\n\n''' + old_shortcut
content = content.replace(old_shortcut, new_shortcut)

# 5. Add activate_select method and update existing ones
old_activate_pen = '''    def activate_pen(self):
        self.engine.use_tool("pen")
        self.btn_pen.setChecked(True)
        self.btn_highlighter.setChecked(False)
        self.btn_eraser.setChecked(False)
        self._recolor_colors_button()'''
new_activate_pen = '''    def activate_pen(self):
        self.engine.use_tool("pen")
        self.btn_pen.setChecked(True)
        self.btn_highlighter.setChecked(False)
        self.btn_eraser.setChecked(False)
        self.btn_select.setChecked(False)
        self._recolor_colors_button()'''
content = content.replace(old_activate_pen, new_activate_pen)

old_activate_highlighter = '''    def activate_highlighter(self):
        self.engine.use_tool("highlighter")
        self.btn_pen.setChecked(False)
        self.btn_highlighter.setChecked(True)
        self.btn_eraser.setChecked(False)
        self._recolor_colors_button()'''
new_activate_highlighter = '''    def activate_highlighter(self):
        self.engine.use_tool("highlighter")
        self.btn_pen.setChecked(False)
        self.btn_highlighter.setChecked(True)
        self.btn_eraser.setChecked(False)
        self.btn_select.setChecked(False)
        self._recolor_colors_button()'''
content = content.replace(old_activate_highlighter, new_activate_highlighter)

old_activate_eraser = '''    def activate_eraser(self):
        self.engine.use_tool("eraser")
        self.btn_pen.setChecked(False)
        self.btn_highlighter.setChecked(False)
        self.btn_eraser.setChecked(True)'''
new_activate_eraser = '''    def activate_eraser(self):
        self.engine.use_tool("eraser")
        self.btn_pen.setChecked(False)
        self.btn_highlighter.setChecked(False)
        self.btn_eraser.setChecked(True)
        self.btn_select.setChecked(False)'''
content = content.replace(old_activate_eraser, new_activate_eraser)

activate_select = '''
    def activate_select(self):
        self.engine.use_tool("selection")
        self.btn_pen.setChecked(False)
        self.btn_highlighter.setChecked(False)
        self.btn_eraser.setChecked(False)
        self.btn_select.setChecked(True)
        self.canvas.update()
'''
content = content.replace(new_activate_eraser, new_activate_eraser + activate_select)

with open('ui/main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Main window updated!")
