from typing import Optional, Dict
from core.notebook import Notebook
from core.page import Page
from core.tools.tool import Tool
from core.tools.pen import Pen
from core.tools.selection import Selection
from core.commands.command_manager import CommandManager

class DrawingEngine:
    def __init__(self, notebook: Notebook, command_manager: CommandManager):
        self.notebook = notebook
        self.command_manager = command_manager
        self.current_page_index = 0
        
        self.tools: Dict[str, Tool] = {
            "pen": Pen(),
            "selection": Selection()
        }
        self.active_tool_name = "pen"

    @property
    def current_page(self) -> Page:
        return self.notebook.pages[self.current_page_index]
        
    @property
    def active_tool(self) -> Tool:
        return self.tools[self.active_tool_name]

    def set_tool(self, tool_name: str, tool: Tool):
        self.tools[tool_name] = tool
        
    def use_tool(self, tool_name: str):
        if tool_name in self.tools:
            # If leaving selection tool, clear selection
            if self.active_tool_name == "selection" and tool_name != "selection":
                self.tools["selection"].selected_indices = []
                self.tools["selection"].state = "IDLE"
            self.active_tool_name = tool_name

    def handle_press(self, x: float, y: float, pressure: float):
        self.active_tool.on_press(x, y, pressure, self.current_page)

    def handle_move(self, x: float, y: float, pressure: float):
        self.active_tool.on_move(x, y, pressure, self.current_page)

    def handle_release(self, x: float, y: float, pressure: float):
        cmd = self.active_tool.on_release(x, y, pressure, self.current_page)
        if cmd:
            self.command_manager.execute(cmd)

    def undo(self):
        self.command_manager.undo()

    def redo(self):
        self.command_manager.redo()
