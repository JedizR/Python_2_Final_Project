"""
FarmQuest: Python Vanilla Terminal Farming RPG
Version: 1.0.0

A text-based farming game with basic RPG elements, rendered in the terminal
using ASCII graphics. Features include farming, resource gathering, and basic
trading mechanics.

The game supports both Windows and Unix-like systems, automatically adapting its
input handling based on the operating system.

Author: Natakorn Wannabovorn
"""

# Libraries Import
import os
import sys
import time
import random
import json
import math
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import logging
from enum import Enum, auto
import atexit

# OS Libraries Import
if os.name == 'nt':
    import msvcrt
else:
    import tty, termios

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='game.log'
)

# Constants for the game
GAME_VERSION = "1.0.0"
SAVE_FOLDER = "saves"
ASSETS_FOLDER = "assets"

# Screen dimensions
SCREEN_WIDTH: int = 100    # Total screen width
SCREEN_HEIGHT: int = 24    # Total screen height
UI_PANEL_WIDTH: int = 32   # Width of the right UI panel
MAIN_AREA_WIDTH: int = SCREEN_WIDTH - UI_PANEL_WIDTH  # Main game area width

# Direction mappings
DIRECTIONS = {
    'w': (0, -1),  # up
    's': (0, 1),   # down
    'a': (-1, 0),  # left
    'd': (1, 0),   # right
}

# Screen regions
class ScreenRegions:
    """Screen regions for easy reference"""
    MAIN_GAME = "main_game"
    UI_PANEL = "ui_panel"
    
    # Main game area boundaries
    MAIN_X_START = 0
    MAIN_X_END = MAIN_AREA_WIDTH
    
    # UI panel boundaries
    UI_X_START = MAIN_AREA_WIDTH
    UI_X_END = SCREEN_WIDTH
    
    # Padding and spacing
    BORDER_PADDING = 2
    UI_PADDING = 1

# Color
class Colors:
    """Color System fro all RGB color"""
    # Reset
    RESET = '\033[0m'
    ENDC = '\033[0m'  # Alias for RESET

    # Text Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    RAPID_BLINK = '\033[6m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKE = '\033[9m'
    DOUBLE_UNDERLINE = '\033[21m'

    # Standard Foreground Colors (Normal)
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    DEFAULT_FG = '\033[39m'

    # Standard Background Colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_DEFAULT = '\033[49m'

    # Bright Foreground Colors
    BRIGHT_BLACK = '\033[90m'  # Gray
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Bright Background Colors
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'

    # Style Reset Codes
    RESET_BOLD = '\033[22m'
    RESET_DIM = '\033[22m'
    RESET_ITALIC = '\033[23m'
    RESET_UNDERLINE = '\033[24m'
    RESET_BLINK = '\033[25m'
    RESET_REVERSE = '\033[27m'
    RESET_HIDDEN = '\033[28m'
    RESET_STRIKE = '\033[29m'

    # Alternative names for better readability
    GRAY = BRIGHT_BLACK
    GREY = BRIGHT_BLACK
    BG_GRAY = BG_BRIGHT_BLACK
    BG_GREY = BG_BRIGHT_BLACK
    INVERT = REVERSE
    CONCEALED = HIDDEN
    CROSSED = STRIKE
    
    @staticmethod
    def rgb_fg(r: int, g: int, b: int) -> str:
        """Create RGB foreground color"""
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def rgb_bg(r: int, g: int, b: int) -> str:
        """Create RGB background color"""
        return f'\033[48;2;{r};{g};{b}m'

    @staticmethod
    def disable_colors():
        """Disable all colors by setting them to empty strings"""
        for attr_name in dir(Colors):
            if (not attr_name.startswith('__') 
                and isinstance(getattr(Colors, attr_name), str)):
                setattr(Colors, attr_name, '')

    @staticmethod
    def demo():
        """Print a demonstration of all colors and styles"""
        # Text styles
        print(f"{Colors.BOLD}Bold{Colors.RESET}")
        print(f"{Colors.DIM}Dim{Colors.RESET}")
        print(f"{Colors.ITALIC}Italic{Colors.RESET}")
        print(f"{Colors.UNDERLINE}Underline{Colors.RESET}")
        print(f"{Colors.BLINK}Blink{Colors.RESET}")
        print(f"{Colors.REVERSE}Reverse{Colors.RESET}")
        print(f"{Colors.HIDDEN}Hidden{Colors.RESET}")
        print(f"{Colors.STRIKE}Strike{Colors.RESET}")
        
        # Standard colors
        print("\nStandard Foreground Colors:")
        for color in ['BLACK', 'RED', 'GREEN', 'YELLOW', 
                      'BLUE', 'MAGENTA', 'CYAN', 'WHITE']:
            print(f"{getattr(Colors, color)}This is {color}{Colors.RESET}")
        
        # Bright colors
        print("\nBright Foreground Colors:")
        for color in ['BRIGHT_BLACK', 'BRIGHT_RED', 
                      'BRIGHT_GREEN', 'BRIGHT_YELLOW', 
                     'BRIGHT_BLUE', 'BRIGHT_MAGENTA', 
                     'BRIGHT_CYAN', 'BRIGHT_WHITE']:
            print(f"{getattr(Colors, color)}This is {color}{Colors.RESET}")
        
        # Background colors
        print("\nBackground Colors:")
        for color in ['BG_BLACK', 'BG_RED', 'BG_GREEN', 'BG_YELLOW', 
                     'BG_BLUE', 'BG_MAGENTA', 'BG_CYAN', 'BG_WHITE']:
            print(f"{getattr(Colors, color)}This is {color}{Colors.RESET}")
        
        # RGB examples
        print("\nRGB Colors Examples:")
        print(f"{Colors.rgb_fg(255, 0, 0)}Red RGB Text{Colors.RESET}")
        print(f"{Colors.rgb_bg(0, 255, 0)}Green RGB Background{Colors.RESET}")

# Frame rate control
class FrameRateController:
    """
    Control frame rate by adding necessary delay.
    """
    def __init__(self, target_fps: int = 30):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.last_frame_time = time.time()

    def tick(self):
        """Control frame rate by adding necessary delay."""
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        if elapsed < self.frame_time:
            time.sleep(self.frame_time - elapsed)
        self.last_frame_time = time.time()

# Screen buffer for efficient rendering
class ScreenBuffer:
    """
    Implementation of the ScreenBuffer from scratches
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.main_area_width = width - UI_PANEL_WIDTH
        self.buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.color_buffer = [[Colors.ENDC for _ in 
                              range(width)] for _ in range(height)]
        
    def clear(self):
        """Clear the screen buffer."""
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = ' '
                self.color_buffer[y][x] = Colors.ENDC
    
    def draw_char(self, x: int, y: int, char: 
        str, color: str = Colors.ENDC):
        """Draw a character at the specified position with optional color."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y][x] = char
            self.color_buffer[y][x] = color

    def draw_string(self, x: int, y: int, string: 
        str, color: str = Colors.ENDC):
        """Draw a string at the specified position with optional color."""
        for i, char in enumerate(string):
            if x + i >= self.width:
                break
            self.draw_char(x + i, y, char, color)
    
    def draw_vertical_line(self, x: int, start_y: 
        int, end_y: int, char: str, color: str = Colors.ENDC):
        """Draw a vertical line."""
        for y in range(start_y, end_y + 1):
            self.draw_char(x, y, char, color)
    
    def draw_horizontal_line(self, y: int, start_x: 
        int, end_x: int, char: str, color: str = Colors.ENDC):
        """Draw a horizontal line."""
        for x in range(start_x, end_x + 1):
            self.draw_char(x, y, char, color)
            
    def is_in_main_area(self, x: int, y: int) -> bool:
        """Check if coordinates are in the main game area."""
        return (ScreenRegions.MAIN_X_START <= x < ScreenRegions.MAIN_X_END and 
                0 <= y < self.height)
    
    def is_in_ui_panel(self, x: int, y: int) -> bool:
        """Check if coordinates are in the UI panel area."""
        return (ScreenRegions.UI_X_START <= x < ScreenRegions.UI_X_END and 
                0 <= y < self.height)

    def render(self):
        """Render the buffer to the terminal."""
        clear_screen()
        for y in range(self.height):
            line = ''
            current_color = Colors.ENDC
            for x in range(self.width):
                if self.color_buffer[y][x] != current_color:
                    current_color = self.color_buffer[y][x]
                    line += current_color
                line += self.buffer[y][x]
            print(line + Colors.ENDC)
      
class UIPanelSection:
    """Represents a section in the UI panel"""
    def __init__(self, title: str, start_y: int, height: int):
        self.title = title
        self.start_y = start_y
        self.height = height
        self.content = []

class UIPanel:
    """Manages the right-side UI panel"""
    def __init__(self):
        self.width = UI_PANEL_WIDTH
        self.x_start = MAIN_AREA_WIDTH - 1  # -1 to overlap with main border
        # Adjusted y-positions and heights for better spacing
        self.sections = {
            'status': UIPanelSection("Status", 3, 4),      # Player status
            'tools': UIPanelSection("Tools", 8, 4),        # Tools
            'inventory': UIPanelSection("Inventory", 13, 6), # Inventory
            'info': UIPanelSection("Info", 20, 3)          # Info
        }

    def draw(self, screen: ScreenBuffer, 
             game_state: Optional[Any] = None):
        """Draw the entire UI panel and its sections"""
        self._draw_sections(screen)
        if game_state:
            self._draw_status(screen, game_state)
            self._draw_tools(screen, game_state)
            self._draw_inventory(screen, game_state)
            self._draw_info(screen, game_state)

    def _draw_section_header(self, screen: ScreenBuffer, 
                             section: UIPanelSection):
        """Draw a section header with title"""
        x_start = self.x_start + 2
        y = section.start_y
        
        # Draw header with decorative formatting
        header = f"─ {section.title} " + "─" * (self.width 
                                                - len(section.title) - 6)
        screen.draw_string(x_start, y, header, Colors.BRIGHT_BLACK)

    def _draw_sections(self, screen: ScreenBuffer):
        """Draw all section borders and headers"""
        for section in self.sections.values():
            self._draw_section_header(screen, section)

    def _draw_status(self, screen: ScreenBuffer, game_state: Any):
        """Draw player status information"""
        section = self.sections['status']
        start_x = self.x_start + 2
        y = section.start_y + 1

        # Draw status items
        screen.draw_string(start_x, y, f"Time: {game_state.get_time_string()}", 
                           Colors.BRIGHT_GREEN)
        screen.draw_string(start_x, y + 1, f"Money: ${game_state.money}", 
                           Colors.BRIGHT_YELLOW)
        screen.draw_string(start_x, y + 2, 
                         f"Energy: {game_state.energy}/{game_state.max_energy}", 
                         Colors.BRIGHT_CYAN)

    def _draw_tools(self, screen: ScreenBuffer, game_state: Any):
        """Draw tool selection and information"""
        section = self.sections['tools']
        start_x = self.x_start + 2
        y = section.start_y + 1

        # Tool list with selection indicators
        tools = [
            ("1", "Axe", game_state.current_tool == ToolType.AXE),
            ("2", "Hoe", game_state.current_tool == ToolType.HOE),
            ("3", "Seeds", game_state.current_tool == ToolType.SEEDS)
        ]

        for i, (key, name, selected) in enumerate(tools):
            color = Colors.BRIGHT_YELLOW if selected else Colors.BRIGHT_WHITE
            tool_text = f"{key}: {name}"
            if selected:
                tool_text = f"{key}: [{name}]"
            screen.draw_string(start_x, y + i, tool_text, color)

    def _draw_inventory(self, screen: ScreenBuffer, game_state: Any):
        """Draw inventory items"""
        section = self.sections['inventory']
        start_x = self.x_start + 2
        y = section.start_y + 1

        # Draw inventory items with proper spacing
        for i, (item, count) in enumerate(game_state.inventory.items()):
            if i >= section.height - 2:  # Leave space for header
                break
            # Format item text with consistent spacing
            item_text = f"{item:<7}: {count:>3}"
            color = Colors.BRIGHT_WHITE
            screen.draw_string(start_x, y + i, item_text, color)

    def _draw_info(self, screen: ScreenBuffer, game_state: Any):
        """Draw context-sensitive information"""
        section = self.sections['info']
        start_x = self.x_start + 2
        y = section.start_y + 1

        # Get current context info (positions etc)
        current_pos = game_state.player_pos
        interact_pos = get_interaction_position(game_state.player_pos, 
                                                game_state.player_direction)
        pos_text = f"({current_pos[0]}, {current_pos[1]})"
        face_text = f"({interact_pos[0]}, {interact_pos[1]})"
        screen.draw_string(start_x, y, f"Position: {pos_text}", 
                           Colors.BRIGHT_WHITE)
        screen.draw_string(start_x, y + 1, f"Face To : {face_text}", 
                           Colors.BRIGHT_WHITE)

    def update_info(self, info_text: List[str]):
        """Update the info section with new text"""
        self.sections['info'].content = info_text

    def get_section_bounds(self, 
                           section_name: str) -> Tuple[int, int, int, int]:
        """Get the bounds (x1, y1, x2, y2) of a section"""
        section = self.sections.get(section_name)
        if not section:
            return (0, 0, 0, 0)
        return (
            self.x_start,
            section.start_y,
            self.x_start + self.width,
            section.start_y + section.height
        )

class MenuItem:
    """
    Represents a menu item with a text label, action, and color.
    """
    def __init__(self, 
                 text: str, 
                 action: str, 
                 color: str = Colors.BRIGHT_WHITE):
        self.text = text
        self.action = action
        self.color = color

class MenuSystem:
    """
    Represents a menu system with a title and a list of menu items.
    """
    def __init__(self, title: str, items: List[MenuItem]):
        self.title = title
        self.items = items
        self.selected_index = 0
        self.animation_frame = 0
        self.frame_count = 0
        self._last_input_time = time.time()
        self._input_cooldown = 0.1
    
    def draw(self, screen: ScreenBuffer):
        """Draw the menu system"""
        self.frame_count += 1
        self.animation_frame = (self.frame_count // 10) % 4
        
        # Clear screen and draw border
        screen.clear()
        self.draw_fancy_border(screen)
        
        # Draw title
        title_lines = self.title.split('\n')
        start_y = 3
        
        # Calculate the maximum title width
        max_title_width = max(len(line) for line in title_lines)
        
        for i, line in enumerate(title_lines):
            # Center each line
            x = (screen.width - len(line)) // 2
            if x >= 0:
                color_cycle = [Colors.BRIGHT_CYAN, Colors.BRIGHT_BLUE, 
                             Colors.BRIGHT_MAGENTA, Colors.BRIGHT_GREEN]
                current_color = color_cycle[self.animation_frame]
                screen.draw_string(x, start_y + i, line, current_color)
        
        # Draw menu items
        menu_start_y = start_y + len(title_lines) + 3
        for i, item in enumerate(self.items):
            text = item.text
            if i == self.selected_index:
                # Animate the selector
                selector = ["→  ", " → ", "  →", " → "][self.animation_frame]
                text = f"{selector}{text}{"  ←"}"
            else:
                text = f"   {text}   "
            
            x = (screen.width - len(text)) // 2
            y = menu_start_y + i * 2
            
            # Set color based on selection
            color = item.color
            if i == self.selected_index:
                color = Colors.BOLD + color
            
            screen.draw_string(x, y, text, color)
        
        # Draw controls help
        controls_text = "↑/W: Up | ↓/S: Down | Enter/Space: Select | Esc: Quit"
        controls_x = (screen.width - len(controls_text)) // 2
        screen.draw_string(
            controls_x,
            screen.height - 4,
            controls_text,
            Colors.BRIGHT_BLACK
        )
        
        # Draw version
        version_text = f"V{GAME_VERSION}"
        screen.draw_string(
            screen.width - len(version_text) - 2,
            screen.height - 2,
            version_text,
            Colors.BRIGHT_BLACK
        )
    
    def draw_fancy_border(self, screen: ScreenBuffer):
        """Draw fancy border around the menu"""
        # Draw corners
        screen.draw_char(0, 0, '╔', Colors.BRIGHT_CYAN)
        screen.draw_char(screen.width - 1, 0, '╗', 
                         Colors.BRIGHT_CYAN)
        screen.draw_char(0, screen.height - 1, '╚', 
                         Colors.BRIGHT_CYAN)
        screen.draw_char(screen.width - 1, screen.height - 1, '╝', 
                         Colors.BRIGHT_CYAN)

        # Draw edges with fancy patterns
        for x in range(1, screen.width - 1):
            pattern_top = '═' if x % 2 == 0 else '╌'
            pattern_bottom = '═' if x % 2 == 0 else '╌'
            screen.draw_char(x, 0, pattern_top, Colors.BRIGHT_CYAN)
            screen.draw_char(x, screen.height - 1, pattern_bottom, 
                             Colors.BRIGHT_CYAN)

        for y in range(1, screen.height - 1):
            pattern_left = '║' if y % 2 == 0 else '│'
            pattern_right = '║' if y % 2 == 0 else '│'
            screen.draw_char(0, y, pattern_left, Colors.BRIGHT_CYAN)
            screen.draw_char(screen.width - 1, y, pattern_right, 
                             Colors.BRIGHT_CYAN)

    def handle_input(self, key: str) -> Optional[str]:
        """Handle menu input and return the new game state if action taken"""
        current_time = time.time()
        if current_time - self._last_input_time < self._input_cooldown:
            return None
            
        self._last_input_time = current_time
        
        if key in ['w', 'W']:
            self.selected_index = (self.selected_index - 1) % len(self.items)
        elif key in ['s', 'S']:
            self.selected_index = (self.selected_index + 1) % len(self.items)
        elif key in ['\r', '\n', ' ']:  # Enter/Return or Space
            if 0 <= self.selected_index < len(self.items):
                return self.items[self.selected_index].action
        elif key == chr(27):  # ESC
            return GameState.QUIT
        return None
  
class MainMenu(MenuSystem):
    """UI for the main menu"""
    def __init__(self):
        title = (
            "███████╗ █████╗ ██████╗ ███╗   ███╗     ██████╗ ██╗   ██╗███████╗███████╗████████╗\n"
            "██╔════╝██╔══██╗██╔══██╗████╗ ████║    ██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝\n"
            "█████╗  ███████║██████╔╝██╔████╔██║    ██║   ██║██║   ██║█████╗  ███████╗   ██║   \n"
            "██╔══╝  ██╔══██║██╔══██╗██║╚██╔╝██║    ██║  ███║██║   ██║██╔══╝  ╚════██║   ██║   \n"
            "██║     ██║  ██║██║  ██║██║ ╚═╝ ██║    ╚███████╝╚██████╔╝███████╗███████║   ██║   \n"
            "╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═════██ ╚═════╝ ╚══════╝╚══════╝   ╚═╝   "
        )
        items = [
            MenuItem("New Game", GameState.PLAYING, Colors.BRIGHT_GREEN),
            MenuItem("Exit", GameState.QUIT, Colors.BRIGHT_RED)
        ]
        super().__init__(title, items)

class PauseMenu(MenuSystem):
    """UI for pause menu"""
    def __init__(self):
        title = (
        "██████╗  █████╗ ██╗   ██╗███████╗███████╗██████╗ "
        "██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝██╔══██╗"
        "██████╔╝███████║██║   ██║███████╗█████╗  ██║  ██║"
        "██╔═══╝ ██╔══██║██║   ██║╚════██║██╔══╝  ██║  ██║"
        "██║     ██║  ██║╚██████╔╝███████║███████╗██████╔╝"
        "╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═════╝ "
        )
        items = [
            MenuItem("Resume", GameState.PLAYING, Colors.BRIGHT_GREEN),
            MenuItem("Main Menu", GameState.MAIN_MENU, Colors.BRIGHT_MAGENTA),
            MenuItem("Exit", GameState.QUIT, Colors.BRIGHT_RED)
        ]
        super().__init__(title, items)

def is_in_main_area(self, x: int, y: int) -> bool:
    """Check if coordinates are in the main game area."""
    return (ScreenRegions.MAIN_X_START <= x < ScreenRegions.MAIN_X_END and 
            0 <= y < self.height)

def is_in_ui_panel(self, x: int, y: int) -> bool:
    """Check if coordinates are in the UI panel area."""
    return (ScreenRegions.UI_X_START <= x < ScreenRegions.UI_X_END and 
            0 <= y < self.height)

class ToolType(Enum):
    """The type of tool"""
    NONE = auto()
    AXE = auto()
    HOE = auto()
    SEEDS = auto()
    WATERING_CAN = auto()

class CropType:
    """The type of crop"""
    WHEAT = "wheat"
    POTATO = "potato"
    TOMATO = "tomato"
    CORN = "corn"

class ItemType:
    """All items types"""
    # Basic items
    WOOD = "wood"
    STONE = "stone"
    SEEDS = "seeds"
    
    # Crops
    WHEAT = "wheat"
    POTATO = "potato"
    CORN = "corn"
    
    # Tools
    AXE = "axe"
    HOE = "hoe"
    WATERING_CAN = "watering_can"
    
    @staticmethod
    def get_base_price(item_type: str) -> int:
        prices = {
            ItemType.WOOD: 5,
            ItemType.STONE: 3,
            ItemType.SEEDS: 10,
            ItemType.WHEAT: 15,
            ItemType.POTATO: 20,
            ItemType.CORN: 25,
            ItemType.AXE: 50,
            ItemType.HOE: 40,
            ItemType.WATERING_CAN: 30,
        }
        return prices.get(item_type, 0)

class ToolStats:
    """Stats for different tool levels"""
    STATS = {
        ToolType.AXE: {
            1: {"damage": 34, "energy": 5},    # Basic axe
            2: {"damage": 50, "energy": 4},    # Better axe
            3: {"damage": 75, "energy": 3},    # Best axe
        },
        ToolType.HOE: {
            1: {"till_speed": 1, "energy": 5}, # Basic hoe
            2: {"till_speed": 2, "energy": 4}, # Better hoe
            3: {"till_speed": 3, "energy": 3}, # Best hoe
        },
    }

class CropData:
    CROPS = {
        CropType.WHEAT: {
            'growth_time': 15,  # Minutes for each stage
            'stages': ['seeds', 'sprout', 'growing', 'ready'],
            'water_needs': 2,   # Water needed per day
            'base_value': 10,   # Base selling price
            'yield': (2, 4),    # Min/max yield
            'symbols': [',', 'ω', 'ϗ', 'Ψ'],
            'colors': [
                Colors.rgb_fg(120, 180, 50),  # Seeds
                Colors.rgb_fg(100, 200, 50),  # Sprout
                Colors.rgb_fg(80, 220, 50),   # Growing
                Colors.rgb_fg(220, 220, 50)   # Ready
            ]
        },
        CropType.POTATO: {
            'growth_time': 20,
            'stages': ['seeds', 'sprout', 'growing', 'ready'],
            'water_needs': 1,
            'base_value': 15,
            'yield': (1, 3),
            'symbols': [',', 'ω', 'ϗ', 'Ψ'],
            'colors': [
                Colors.rgb_fg(120, 180, 50),
                Colors.rgb_fg(100, 200, 50),
                Colors.rgb_fg(80, 220, 50),
                Colors.rgb_fg(180, 140, 80)
            ]
        }
    }

class Crop:
    def __init__(self, crop_type: str):
        self.type = crop_type
        self.info = CropInfo.CROPS[crop_type]
        self.stage = CropStage.SEEDS
        self.growth_time = 0
        self.watered = False
        
    def update(self, minutes_passed: int) -> bool:
        """Update crop growth. Returns True if stage changed."""
        if self.stage == CropStage.READY:
            return False
            
        if self.watered:
            self.growth_time += minutes_passed
            if self.growth_time >= self.info['growth_time']:
                self.growth_time = 0
                if self.stage != CropStage.READY:
                    self.stage = CropStage(self.stage.value + 1)
                    return True
        return False
        
    def get_display(self) -> Tuple[str, str]:
        """Get current display character and color."""
        symbol, color = self.info['stages'][self.stage.value]
        if not self.watered:
            # Make color more muted if not watered
            color = Colors.DIM + color
        return symbol, color

class CropStage(Enum):
    SEEDS = auto()
    SPROUT = auto()
    GROWING = auto()
    READY = auto()

class CropInfo:
    CROPS = {
        'wheat': {
            'growth_time': 10,  # Minutes per stage
            'sell_price': 15,
            'stages': [
                ('·', Colors.BRIGHT_GREEN),  # Seeds
                ('∴', Colors.BRIGHT_GREEN),  # Sprout
                ('ω', Colors.GREEN),         # Growing
                ('Ψ', Colors.BRIGHT_YELLOW)  # Ready
            ],
            'name': 'Wheat'
        },
        'corn': {
            'growth_time': 15,
            'sell_price': 25,
            'stages': [
                ('·', Colors.BRIGHT_GREEN),  # Seeds
                ('∵', Colors.BRIGHT_GREEN),  # Sprout
                ('φ', Colors.GREEN),         # Growing
                ('¥', Colors.BRIGHT_YELLOW)  # Ready
            ],
            'name': 'Corn'
        }
    }

@dataclass
class GameObject:
    x: int
    y: int
    tile_type: str
    health: int = 100
    growth_time: int = 0
    growth_stage: int = 0
    water_level: int = 0
    quality: int = 1
    durability: Optional[int] = None
    regrowth_time: Optional[int] = None

    def update(self, game_state: 'EnhancedGameState') -> bool:
        """Update object state, return True if state changed"""
        current_time = game_state.time_hours * 60 + game_state.time_minutes

        # Handle tree stump regrowth
        if self.tile_type == 'stump' and self.regrowth_time is not None:
            if current_time >= self.regrowth_time:
                self.tile_type = 'tree'
                self.health = 100
                self.regrowth_time = None
                return True

        return False

    def can_interact(self) -> bool:
        """Check if object can be interacted with"""
        try:
            if self.tile_type == 'tree':
                return self.health > 0
            elif self.tile_type == 'farm_plot':
                return True
            elif self.tile_type == 'crops_ready':
                return True
            elif self.tile_type == 'stump':
                return False
            return False
        except:
            return False

    def get_interaction_text(self, 
                             game_state: 'EnhancedGameState') -> str:
        """Get text describing possible interaction"""
        try:
            if self.tile_type == 'tree':
                return f"Tree: {self.health}% (Use axe)" if self.health > 0 else "Tree stump"
            elif self.tile_type == 'stump':
                if self.regrowth_time is not None:
                    current_time = (game_state.time_hours 
                                    * 60 + game_state.time_minutes)
                    minutes_left = max(0, self.regrowth_time - current_time)
                    return f"Regrows in {minutes_left}m"
                return "Tree stump"
            elif self.tile_type == 'farm_plot':
                return "Use seeds to plant"
            elif self.tile_type == 'crops_ready':
                return "Press F to harvest"
            return ""
        except:
            return ""

    def apply_tool(self, 
                   tool_type: ToolType, 
                   game_state: 'EnhancedGameState') -> bool:
        """Apply tool effect to object, return True if successful"""
        try:
            if tool_type == ToolType.AXE and self.tile_type == 'tree':
                # Damage tree
                old_health = self.health
                self.health = max(0, self.health - 34)
                
                if self.health <= 0:
                    # Tree has been cut down - turn into stump
                    wood_amount = random.randint(2, 4)
                    game_state.add_item('wood', wood_amount)
                    self.tile_type = 'stump'
                    # Set regrowth time to 1 hour from now
                    current_time = (game_state.time_hours 
                                    * 60 + game_state.time_minutes)
                    self.regrowth_time = current_time + 60 
                    game_state.set_status(f"Got {wood_amount} wood! Tree will regrow in 1 hour.", 
                                          Colors.BRIGHT_GREEN, 45)
                    return True
                else:
                    game_state.set_status(f"Tree health: {self.health}%", 
                                          Colors.BRIGHT_YELLOW, 30)
                    return old_health != self.health
                    
            elif tool_type == ToolType.HOE:
                if self.tile_type == 'grass':
                    self.tile_type = 'farm_plot'
                    self.water_level = 0
                    game_state.set_status("Created farm plot!", 
                                          Colors.BRIGHT_GREEN, 30)
                    return True
            
            elif tool_type == ToolType.SEEDS and self.tile_type == 'farm_plot':
                if game_state.inventory.get('seeds', 0) > 0:
                    self.tile_type = 'crops_seeds'
                    self.growth_time = 0
                    game_state.remove_item('seeds', 1)
                    game_state.set_status("Planted seeds!", 
                                          Colors.BRIGHT_GREEN, 30)
                    return True
                else:
                    game_state.set_status("No seeds!", 
                                          Colors.BRIGHT_RED, 30)
                    return False
                    
            return False
            
        except Exception as e:
            logging.error(f"Error in apply_tool: {str(e)}")
            return False

# Game states
class GameState:
    MAIN_MENU = "main_menu"
    LOADING = "loading"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    FARMING = "farming"
    HOUSE = "house"
    MINE = "mine"
    ADVENTURE = "adventure"
    COMBAT = "combat"
    SETTINGS = "settings"
    SAVING = "saving"
    CREDITS = "credits"
    QUIT = "quit"

    @staticmethod
    def is_game_active(state: str) -> bool:
        """Check if the given state is an active gameplay state"""
        return state in [GameState.PLAYING, GameState.FARMING, 
                        GameState.HOUSE, GameState.MINE, 
                        GameState.ADVENTURE, GameState.COMBAT]
        
class PlayerDirection(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class EnhancedGameState:
    def __init__(self):
        # Player state
        self.player_pos = [50, 10]  # Center of map initially
        self.player_direction = PlayerDirection.DOWN
        self.energy = 150
        self.max_energy = 150
        self.money = 100
        self.experience = 0
        
        # Tool and inventory system
        self.current_tool = ToolType.NONE
        self.inventory = {
            'wood': 0,
            'stone': 0,
            'seeds': 0,
            'crops': 0,
        }
        self.tools = {
            ToolType.AXE: True,      # Player starts with an axe
            ToolType.HOE: True,      # and a hoe
            ToolType.SEEDS: False,   # needs to be bought/found
            ToolType.WATERING_CAN: False
        }
        
        # World state
        self.time_hours = 6  # Game starts at 6 AM
        self.time_minutes = 0
        self.day = 1
        self.inside_house = False
        self.show_minimap = True
        
        # Status message system
        self.status_message = ""
        self.status_color = Colors.BRIGHT_WHITE
        self.status_timeout = 0
        
        # Object tracking
        self.objects = {}
        self.crops = {} 

    def set_status(self, message: str, 
                   color: str = Colors.BRIGHT_WHITE, 
                   timeout: int = 60):
        """Set a status message with optional color and timeout (in frames)."""
        self.status_message = message
        self.status_color = color
        self.status_timeout = timeout

    def update_status(self):
        """Update status message timeout."""
        if self.status_timeout > 0:
            self.status_timeout -= 1
            if self.status_timeout == 0:
                self.status_message = ""
                self.status_color = Colors.BRIGHT_WHITE

    def update_time(self, minutes_passed: int):
        """Update game time by specified minutes"""
        self.time_minutes += minutes_passed
        while self.time_minutes >= 60:
            self.time_minutes -= 60
            self.time_hours += 1
        
        if self.time_hours >= 24:
            self.time_hours = 0
            self.day += 1

    def get_time_string(self) -> str:
        """Get formatted time string"""
        period = "AM" if self.time_hours < 12 else "PM"
        hour = self.time_hours if self.time_hours <= 12 else self.time_hours-12
        if hour == 0:
            hour = 12
        return f"{hour:02d}:{self.time_minutes:02d} {period}"

    def use_energy(self, amount: int) -> bool:
        """Try to use energy and return whether successful"""
        if self.energy >= amount:
            self.energy -= amount
            return True
        self.set_status("Too tired!", Colors.BRIGHT_RED, 30)
        return False

    def add_item(self, item: str, amount: int = 1):
        """Add an item to inventory"""
        if item in self.inventory:
            self.inventory[item] += amount
        else:
            self.inventory[item] = amount
        self.set_status(f"Got {amount} {item}!", Colors.BRIGHT_GREEN, 30)

    def remove_item(self, item: str, amount: int = 1) -> bool:
        """Remove an item from inventory if possible"""
        if item in self.inventory and self.inventory[item] >= amount:
            self.inventory[item] -= amount
            if self.inventory[item] == 0:
                del self.inventory[item]
            return True
        self.set_status(f"Not enough {item}!", Colors.BRIGHT_RED, 30)
        return False

    def select_tool(self, tool_type: ToolType) -> bool:
        """Try to select a tool and return whether successful"""
        if tool_type in self.tools and self.tools[tool_type]:
            self.current_tool = tool_type
            return True
        return False

    def can_afford(self, cost: int) -> bool:
        """Check if player can afford a purchase"""
        return self.money >= cost

    def add_object(self, x: int, y: int, obj_type: str):
        """Add an object to the game world"""
        key = (x, y)
        self.objects[key] = GameObject(x, y, obj_type)

    def remove_object(self, x: int, y: int):
        """Remove an object from the game world"""
        key = (x, y)
        if key in self.objects:
            del self.objects[key]

    def get_object(self, x: int, y: int) -> Optional[GameObject]:
        """Get object at specified position"""
        return self.objects.get((x, y))

    def is_position_walkable(self, x: int, y: int) -> bool:
        """Check if a position is walkable"""
        # Check if position is within map bounds
        if not (0 <= y < len(VILLAGE_MAP) and 0 <= x 
                < len(VILLAGE_MAP[0])):
            return False

        # Check map tile
        map_char = VILLAGE_MAP[y][x]
        if map_char in 'HTMfs~':
            return False

        # Check objects
        obj = self.get_object(x, y)
        if obj:
            return obj.tile_type in ['farm_plot', 
                                     'crops_seeds', 
                                     'crops_growing', 
                                     'crops_ready']

        return True

    def handle_tool_use(self, target_x: int, 
                        target_y: int) -> bool:
        """Handle tool usage at target position"""
        try:
            # Check if tool is selected
            if self.current_tool == ToolType.NONE:
                self.set_status("No tool selected!", 
                                Colors.BRIGHT_RED, 30)
                return False

            # Check if target position is valid
            if not (0 <= target_y < len(VILLAGE_MAP) 
                    and 0 <= target_x < len(VILLAGE_MAP[0])):
                self.set_status("Can't use tool here!", Colors.BRIGHT_RED, 30)
                return False

            # Get or create game object
            target_pos = (target_x, target_y)
            obj = self.get_object(target_x, target_y)
            
            # Handle tree creation if needed
            if not obj and VILLAGE_MAP[target_y][target_x] == 'T':
                self.add_object(target_x, target_y, 'tree')
                obj = self.get_object(target_x, target_y)
                logging.info(f"Created new tree object at {target_x}, {target_y}")

            # Apply tool to object
            if obj:
                success = obj.apply_tool(self.current_tool, self)
                if success:
                    logging.info(f"Tool {self.current_tool.name} used successfully on {obj.tile_type}")
                return success

            # Handle empty tile tool usage
            if self.current_tool == ToolType.HOE:
                if VILLAGE_MAP[target_y][target_x] == 'G':  # grass
                    self.add_object(target_x, target_y, 'farm_plot')
                    logging.info(f"Created new farm plot at {target_x}, {target_y}")
                    return True

            self.set_status("Can't use tool here!", Colors.BRIGHT_RED, 30)
            return False
            
        except Exception as e:
            logging.error(f"Error in handle_tool_use: {str(e)}")
            self.set_status("Tool use failed!", Colors.BRIGHT_RED, 30)
            return False

# Cross-platform input handling
class InputHandler:
    def __init__(self):
        self.is_windows = os.name == 'nt'
        if not self.is_windows:
            self.fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)
    
    def getch(self) -> str:
        """Get a single character from input without requiring Enter."""
        if self.is_windows:
            # Windows input handling
            if msvcrt.kbhit():
                try:
                    ch = msvcrt.getch()
                    # Handle special keys
                    if ch in [b'\x00', b'\xe0']:  # Arrow keys prefix
                        ch2 = msvcrt.getch()
                        if ch2 == b'H':  # Up arrow
                            return 'w'
                        elif ch2 == b'P':  # Down arrow
                            return 's'
                        return ''
                    return ch.decode('utf-8')
                except:
                    return ''
            return ''
        else:
            # Unix input handling
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                # Handle escape sequences
                if ch == '\x1b':
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        if ch3 == 'A':  # Up arrow
                            return 'w'
                        elif ch3 == 'B':  # Down arrow
                            return 's'
                        return ''
                return ch
            except:
                return ''
            finally:
                termios.tcsetattr(self.fd, 
                                  termios.TCSADRAIN, 
                                  self.old_settings)
                
    def cleanup(self):
        """Cleanup function to restore terminal settings."""
        if not self.is_windows:
            termios.tcsetattr(self.fd, 
                              termios.TCSADRAIN, 
                              self.old_settings)

# Utility functions for terminal handling
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_size() -> Tuple[int, int]:
    """Get the current terminal size."""
    try:
        columns, rows = os.get_terminal_size()
        return columns, rows
    except:
        return SCREEN_WIDTH, SCREEN_HEIGHT

# Save/Load handling
def ensure_save_directory():
    """Ensure the save directory exists."""
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

def save_game(game_state: Dict, filename: str) -> bool:
    """Save the game state to a file."""
    ensure_save_directory()
    full_path = os.path.join(SAVE_FOLDER, f"{filename}.save")
    try:
        with open(full_path, 'wb') as f:
            pickle.dump(game_state, f)
        logging.info(f"Game saved successfully to {full_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving game: {e}")
        return False

def load_game(filename: str) -> Optional[Dict]:
    """Load a game state from a file."""
    full_path = os.path.join(SAVE_FOLDER, f"{filename}.save")
    try:
        with open(full_path, 'rb') as f:
            game_state = pickle.load(f)
        logging.info(f"Game loaded successfully from {full_path}")
        return game_state
    except Exception as e:
        logging.error(f"Error loading game: {e}")
        return None

# Asset loading
def load_ascii_art(filename: str) -> str:
    """Load ASCII art from the assets folder."""
    try:
        with open(os.path.join(ASSETS_FOLDER, filename), 'r', 
                  encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error loading ASCII art: {e}")
        return ""

# Initialize global input handler
input_handler = InputHandler()
frame_controller = FrameRateController(30)
screen_buffer = ScreenBuffer(SCREEN_WIDTH, SCREEN_HEIGHT)

# Cleanup function to be called on game exit
def cleanup():
    """Cleanup function to be called when the game exits."""
    input_handler.cleanup()
    logging.info("Game shutting down cleanly")

# Register cleanup function
atexit.register(cleanup)

def draw_status_line(screen: ScreenBuffer, 
                     game_state: EnhancedGameState):
    """Draw the status line with current action hints and messages."""
    # Get available width for status line (excluding borders)
    available_width = MAIN_AREA_WIDTH - 4
    
    # Prepare different components of the status line
    controls = []
    
    # Add contextual controls based on current state
    if game_state.current_tool != ToolType.NONE:
        controls.append(("SPACE", f"Use {game_state.
                         current_tool.name.lower()}"))
    
    # Check what's in front of the player
    interact_pos = get_interaction_position(game_state.player_pos, 
                                            game_state.player_direction)
    obj = game_state.get_object(*interact_pos)
    if obj and obj.can_interact():
        if obj.tile_type == 'crops_ready':
            controls.append(("F", "Harvest"))
        elif obj.tile_type == 'tree':
            controls.append(("1", "Equip axe"))
        elif obj.tile_type == 'farm_plot':
            controls.append(("3", "Plant seeds"))

    # Always show basic controls if there's room
    controls.extend([
        ("M", "Map"),
        ("Q", "Quit")
    ])

    # Prepare the control text
    control_text = " | ".join(f"{key}: {action}" for key, action in controls)
    
    # If there's a status message, show it instead of or alongside controls
    if game_state.status_message:
        # Calculate space needed for both
        message_space = len(game_state.status_message) + 2
        controls_space = len(control_text) + 2
        
        if message_space + controls_space <= available_width:
            # Show both if they fit
            screen.draw_string(2, screen.height - 2, 
                               game_state.status_message, 
                               game_state.status_color)
            screen.draw_string(MAIN_AREA_WIDTH - 2 - len(control_text), 
                               screen.height - 2, 
                             control_text, Colors.BRIGHT_WHITE)
        else:
            # Alternate between message and controls based on timeout
            if game_state.status_timeout > 30:
                screen.draw_string(2, screen.height - 2, 
                                   game_state.status_message, 
                                   game_state.status_color)
            else:
                screen.draw_string(2, screen.height - 2, 
                                   control_text, Colors.BRIGHT_WHITE)
    else:
        # Just show controls if no status message
        screen.draw_string(2, screen.height - 2, 
                           control_text, Colors.BRIGHT_WHITE)

def draw_border(screen: ScreenBuffer):
    """Draw borders around both the main game area and UI panel."""
    # Draw main game area border
    # Draw horizontal borders for main area
    for x in range(MAIN_AREA_WIDTH):
        screen.draw_char(x, 0, '═', Colors.YELLOW)  # Top border
        screen.draw_char(x, screen.height - 1, '═', 
                         Colors.YELLOW)  # Bottom border
    
    # Draw vertical borders for main area
    for y in range(screen.height):
        screen.draw_char(0, y, '║', Colors.YELLOW)  # Left border
        screen.draw_char(MAIN_AREA_WIDTH - 1, y, '║', 
                         Colors.YELLOW)  # Right border

    # Draw UI panel border
    # Draw horizontal borders for UI panel
    for x in range(MAIN_AREA_WIDTH - 1, screen.width):
        screen.draw_char(x, 0, '═', Colors.YELLOW)  # Top border
        screen.draw_char(x, screen.height - 1, '═', 
                         Colors.YELLOW)  # Bottom border
    
    # Draw vertical border for UI panel
    for y in range(screen.height):
        screen.draw_char(screen.width - 1, y, '║', 
                         Colors.YELLOW)  # Right border
    
    # Draw corners for main game area
    screen.draw_char(0, 0, '╔', Colors.YELLOW)  # Top-left
    screen.draw_char(MAIN_AREA_WIDTH - 1, 0, 
                     '╗', Colors.YELLOW)  # Top-right
    screen.draw_char(0, screen.height - 1, 
                     '╚', Colors.YELLOW)  # Bottom-left
    screen.draw_char(MAIN_AREA_WIDTH - 1, 
                     screen.height - 1, '╝', 
                     Colors.YELLOW)  # Bottom-right

    # Draw corners for UI panel
    screen.draw_char(MAIN_AREA_WIDTH - 1, 
                     0, '╔', Colors.YELLOW)  # Top-left
    screen.draw_char(screen.width - 1, 
                     0, '╗', Colors.YELLOW)  # Top-right
    screen.draw_char(MAIN_AREA_WIDTH - 1, 
                     screen.height - 1, '╚', Colors.YELLOW)  # Bottom-left
    screen.draw_char(screen.width - 1, 
                     screen.height - 1, '╝', Colors.YELLOW)  # Bottom-right

    # Fix the intersection of borders
    screen.draw_char(MAIN_AREA_WIDTH - 1, 
                     0, '╦', Colors.YELLOW)  # Top intersection
    screen.draw_char(MAIN_AREA_WIDTH - 1, 
                     screen.height - 1, '╩', Colors.YELLOW)  # Bottom intersect

class Tiles:
    GRASS = ('·', Colors.rgb_fg(1, 100, 41) 
             + Colors.rgb_bg(150, 210, 100))
    DIRT = ('░', Colors.rgb_fg(176, 112, 66) 
            + Colors.rgb_bg(120, 91, 60))
    WATER = ('~', Colors.rgb_fg(45, 82, 233) 
             + Colors.rgb_bg(152, 209, 255))
    HOUSE_WALL = ('█', Colors.rgb_fg(112, 69, 33) 
                  + Colors.rgb_bg(150, 210, 100))
    SHOP_WALL = ('█', Colors.rgb_fg(140, 69, 33) 
                 + Colors.rgb_bg(150, 210, 100))
    HOUSE_DOOR = ('▢', Colors.rgb_fg(1, 100, 41) 
                  + Colors.rgb_bg(150, 210, 100))
    HOUSE_WINDOW = ('◆', Colors.rgb_fg(1, 100, 41) 
                    + Colors.rgb_bg(150, 210, 100))
    TREE = ('♣', Colors.rgb_fg(1, 100, 41) 
            + Colors.rgb_bg(150, 210, 100))
    STUMP = ('╥', Colors.rgb_fg(112, 69, 33) 
             + Colors.rgb_bg(150, 210, 100))
    CROPS_SEEDS = (',', Colors.rgb_fg(1, 100, 41) 
                   + Colors.rgb_bg(150, 210, 100))
    CROPS_GROWING = ('ω', Colors.rgb_fg(1, 100, 41) 
                     + Colors.rgb_bg(150, 210, 100))
    CROPS_READY = ('Ψ', Colors.rgb_fg(1, 100, 41) 
                   + Colors.rgb_bg(150, 210, 100))
    PATH = ('≡', Colors.rgb_fg(120, 120, 120) 
            + Colors.rgb_bg(160, 160, 160))
    FENCE = ('+', Colors.rgb_fg(46, 29, 17) 
             + Colors.rgb_bg(150, 210, 100))
    PLAYER = ('▲▶▼◀', Colors.rgb_fg(255, 0, 0))
    WATER_LILY = ('*', Colors.rgb_fg(254, 147, 147) 
                  + Colors.rgb_bg(152, 209, 255))
    MOUNTAIN = ('█', Colors.rgb_fg(100, 100, 100) 
                + Colors.rgb_bg(150, 210, 100))
    PORTAL = ('꩜', Colors.rgb_fg(255, 0, 255))
    MINE_ENTRANCE = ('█', Colors.rgb_fg(60, 60, 60) 
                     + Colors.rgb_bg(60, 60, 60))
    
def convert_map_char_to_tile(char: str) -> Tuple[str, str]:
    """Convert map character to tile symbol and color."""
    mapping = {
        'G': Tiles.GRASS,
        'D': Tiles.HOUSE_DOOR,
        'W': Tiles.HOUSE_WINDOW,
        'H': Tiles.HOUSE_WALL,
        'T': Tiles.TREE,
        'F': Tiles.DIRT,
        'S': Tiles.CROPS_SEEDS,
        'P': Tiles.PATH,
        '~': Tiles.WATER,
        '*': Tiles.WATER_LILY,
        '@': Tiles.PLAYER,
        'M': Tiles.MOUNTAIN,
        'f': Tiles.FENCE,
        's': Tiles.SHOP_WALL,
        'p': Tiles.PORTAL,
        'm': Tiles.MINE_ENTRANCE,
    }
    return mapping.get(char, Tiles.GRASS)

VILLAGE_MAP = [
    "MMMMGGGGGGGGGGGfFFFFFFFFFFFF~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MMMGGGGGGGGGGGGfFFFFFFFFFFFFFF~*~~~~~~~GGGGGGGHHHHHHHHHHHGGGGGGGGGGGGGGGGGGGGG",
    "MMMGGGTGGGGGGGGffFFFFFFFFFFFFF~~~~~~~~~GGGGGGGHHHHHHHHHHHGGGGGGGGGssssssssGGGG",
    "MMGGGGGGGGGGGGGGfFFFFFFFFFFFFFF~~~~~~~~~GGGGGGHHHHHHHHHHHGGGGGGGGGssssssssGGGG",
    "MMGGTGGGGTGGGGGGGffFFFFFFFFFFFF~~~~~~~*~GGGGGGGGGGGGGGGGGGGGGGGGGGssssssssGGGG",
    "MGGGGGGGGGGGGGGGGGffffGGGffffff~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MGGGGGTGGGGGGGGGGGGGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MMGTGGGGGGGGGGGGGGGGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGTTGGGGGGGGGGGGGG",
    "MMGGGGGGGGGTGGGGGGTGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MTTGTGGGGGTGGGGGGGGGGGGGGGGGGGPPPPPPPPPGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MGGTGGGTGGGGGGGGTGGGGGGGGGGGGGPPPPPPPPPGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MMGGGGGGGGGGGGGGGTTGGGGGGGGGGGPPPPPPPPPGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MMMGTTTTGGGGGGGGGGGGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MMMGGGGGGGTTTTTGGGGGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGTGGGGGGGGGGGGGGGGG",
    "MMMGGGGGGGGGGGGGGGGGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MMGTTTTTTGGGGGGGGGGGGGGGGGGGGGGG~~~~*~~~~GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MMGGGTTGGGGGGGGTTTGGGGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGpppppGGGGGGGGGGGGG",
    "MMMGGGGGGTTGGGGGGTTGGGGGGGGTGGGGG~~~~~~~~~GGGGGGGGGGGGGGTGGpppppppGGGGGGGGGGGG",
    "MMMGGTTTTTTTGGGGGGGTTTGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGpppppppppGGGGGGGGGGG",
    "MMMMGGGGTTTGGGGGGTTTTGGGGGGGGGGGGG~*~~~~~~~GGGGGGGGGGGGGGGpppppppppGGGGGGGGGGG",
    "MMMMGTTTGGGGGGGGGGGGGGGGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGpppppppGGGGGGGGGGGG",
    "MMMMGGGGGTTTTGGGGTTGGGGGGGGGGGGGGG~~~~~*~~~GGGGGGGGGGGGGGGGTpppppGGGGGGGGGGGGG",
    "MMMMMGGGGGGGTTTTTGGGGGGGGGGGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "MMMMMMMGGTTGTTTTTGTTGGTTGGGGTGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGGTGGGGGGGG",
    "MMMMMMMGGGTTTTGGGTTTTTTGGGTTGGGGGGGGG~*~~~~~~~GGGGGGGGGTTGGGGGGGGGGGGGGGGGGGGG",
    "MMMMMMMmmmmmmMMMMMMMMMMMMMGGTTTGGGGTGGG~~~~~~~~~GGGGGGGGGGGGGGGGTGGGGGGGGGGGGG",
    "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMGGGGGGG~~~~~~~~~GGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
]

def calculate_camera_offset(player_pos: List[int], 
                            map_width: int, 
                            map_height: int,
                          screen_width: int, 
                          screen_height: int) -> Tuple[int, int]:
    """Calculate camera offset to keep player centered."""
    # Calculate the ideal camera position (player at center)
    camera_x = player_pos[0] - (screen_width - 4) // 2  # -4 for borders
    camera_y = player_pos[1] - (screen_height - 4) // 2  # -4 for borders

    # Clamp camera position to map bounds
    camera_x = max(0, min(camera_x, map_width - (screen_width - 4)))
    camera_y = max(0, min(camera_y, map_height - (screen_height - 4)))

    return -camera_x, -camera_y

def draw_village_map(screen: ScreenBuffer, 
                     game_state: EnhancedGameState):
    """Draw the visible portion of village map with the player centered."""
    map_height = len(VILLAGE_MAP)
    map_width = len(VILLAGE_MAP[0])
    
    # Calculate camera offset to center on player
    offset_x, offset_y = calculate_camera_offset(
        game_state.player_pos,
        map_width,
        map_height,
        MAIN_AREA_WIDTH,  # Use main game area width
        screen.height
    )

    # Calculate visible range
    start_y = max(0, -offset_y - 2)
    end_y = min(map_height, -offset_y + screen.height - 2)
    start_x = max(0, -offset_x - 2)
    end_x = min(map_width, -offset_x + MAIN_AREA_WIDTH - 2)

    # Draw the visible portion of the map
    for y in range(start_y, end_y):
        map_row = VILLAGE_MAP[y]
        for x in range(start_x, end_x):
            if 0 <= x < len(map_row):
                screen_x = x + offset_x + 2  # +2 for border
                screen_y = y + offset_y + 2  # +2 for border
                
                # Only draw if within main game area bounds
                if (2 <= screen_x < MAIN_AREA_WIDTH - 2 and 
                    2 <= screen_y < screen.height - 2):
                    # Draw base terrain
                    symbol, color = convert_map_char_to_tile(map_row[x])
                    screen.draw_char(screen_x, screen_y, symbol, color)

                    # Draw any objects at this position
                    obj = game_state.get_object(x, y)
                    if obj:
                        symbol, color = getattr(Tiles, obj.tile_type.upper())
                        screen.draw_char(screen_x, screen_y, symbol, color)

    # Draw the player
    player_screen_x = game_state.player_pos[0] + offset_x + 2
    player_screen_y = game_state.player_pos[1] + offset_y + 2
    if (2 <= player_screen_x < MAIN_AREA_WIDTH - 2 and 
        2 <= player_screen_y < screen.height - 2):
        player_chars = ('▲', '▶', '▼', '◀')  # Direction characters
        player_char = player_chars[game_state.player_direction.value]
        screen.draw_char(
            player_screen_x, 
            player_screen_y, 
            player_char,
            Colors.rgb_fg(255, 0, 0)
        )

    # Draw minimap if enabled
    if game_state.show_minimap:
        draw_minimap(screen, game_state)

def handle_gameplay_input(game_state: EnhancedGameState, key: str):
    """Handle all gameplay-related input"""
    try:
        if key in DIRECTIONS:
            # Update direction first
            if key == 'w':
                game_state.player_direction = PlayerDirection.UP
            elif key == 'd':
                game_state.player_direction = PlayerDirection.RIGHT
            elif key == 's':
                game_state.player_direction = PlayerDirection.DOWN
            elif key == 'a':
                game_state.player_direction = PlayerDirection.LEFT

            # Then try to move in that direction
            dx, dy = DIRECTIONS[key]
            new_x = game_state.player_pos[0] + dx
            new_y = game_state.player_pos[1] + dy
            
            # Try to move
            if game_state.is_position_walkable(new_x, new_y):
                game_state.player_pos[0] = new_x
                game_state.player_pos[1] = new_y
                if game_state.use_energy(1):
                    game_state.update_time(1)
            else:
                handle_collision(game_state, new_x, new_y)
        
        # Rest of the input handling...
        elif key in '12345':
            handle_tool_selection(game_state, key)
        elif key == ' ':
            handle_tool_use(game_state)
        elif key == 'm':
            game_state.show_minimap = not game_state.show_minimap
            if game_state.show_minimap:
                status = "Minimap shown"
            else:
                status = "Minimap hidden"
            game_state.set_status(status, Colors.BRIGHT_GREEN, 30)
        elif key == 'f':
            handle_interaction(game_state,'f')
            
    except Exception as e:
        logging.error(f"Error in gameplay input: {str(e)}")
        game_state.set_status("Input error!", Colors.BRIGHT_RED, 30)

def draw_minimap(screen: ScreenBuffer, game_state: EnhancedGameState):
    """Draw a small minimap in the corner with current area view."""
    if not game_state.show_minimap:
        return
        
    # Minimap dimensions and position (moved to top-left corner)
    minimap_width = 12
    minimap_height = 6
    minimap_x = 3  # Left margin
    minimap_y = 3  # Top margin after title
    
    # Create background for minimap area
    for y in range(minimap_height + 2):  # +2 for borders
        for x in range(minimap_width + 2):  # +2 for borders
            screen.draw_char(minimap_x - 1 + x, 
                             minimap_y - 1 + y, ' ', 
                             Colors.BG_BLACK)
    
    # Draw minimap border
    screen.draw_char(minimap_x - 1, 
                     minimap_y - 1, 
                     '╔', Colors.BRIGHT_BLACK)
    screen.draw_char(minimap_x + 
                     minimap_width, minimap_y - 1, 
                     '╗', Colors.BRIGHT_BLACK)
    screen.draw_char(minimap_x - 1, 
                     minimap_y + minimap_height, 
                     '╚', Colors.BRIGHT_BLACK)
    screen.draw_char(minimap_x + 
                     minimap_width, minimap_y + minimap_height, 
                     '╝', Colors.BRIGHT_BLACK)
    
    # Draw horizontal borders
    for x in range(minimap_width):
        screen.draw_char(minimap_x + x, 
                         minimap_y - 1, '═', 
                         Colors.BRIGHT_BLACK)
        screen.draw_char(minimap_x + x, 
                         minimap_y + minimap_height, '═', 
                         Colors.BRIGHT_BLACK)
    
    # Draw vertical borders
    for y in range(minimap_height):
        screen.draw_char(minimap_x - 1, 
                         minimap_y + y, 
                         '║', 
                         Colors.BRIGHT_BLACK)
        screen.draw_char(minimap_x + minimap_width, 
                         minimap_y + y, 
                         '║', 
                         Colors.BRIGHT_BLACK)

    # Draw minimap content
    map_height = len(VILLAGE_MAP)
    map_width = len(VILLAGE_MAP[0])
    
    # Calculate map scaling
    scale_x = map_width / minimap_width
    scale_y = map_height / minimap_height
    
    # Draw map content
    for y in range(minimap_height):
        for x in range(minimap_width):
            map_x = int(x * scale_x)
            map_y = int(y * scale_y)
            
            if map_y < map_height and map_x < map_width:
                char = VILLAGE_MAP[map_y][map_x]
                if char == 'H':
                    screen.draw_char(minimap_x + x, 
                                     minimap_y + y, 
                                     '■', 
                                     Colors.RED)
                elif char == '~':
                    screen.draw_char(minimap_x + x, 
                                     minimap_y + y, 
                                     '≈', 
                                     Colors.BRIGHT_BLUE)
                elif char == 'T':
                    screen.draw_char(minimap_x + x, 
                                     minimap_y + y, 
                                     '♣', 
                                     Colors.GREEN)
                elif char == 'P':
                    screen.draw_char(minimap_x + x, 
                                     minimap_y + y, 
                                     '=', 
                                     Colors.YELLOW)
                elif char == 'F':
                    screen.draw_char(minimap_x + x, 
                                     minimap_y + y, 
                                     '#', 
                                     Colors.YELLOW)
                else:
                    screen.draw_char(minimap_x + x, 
                                     minimap_y + y, 
                                     '·', 
                                     Colors.BRIGHT_BLACK)

    # Draw player position
    minimap_player_x = minimap_x + int(game_state.player_pos[0] 
                                       * minimap_width / map_width)
    minimap_player_y = minimap_y + int(game_state.player_pos[1] 
                                       * minimap_height / map_height)
    if (minimap_x <= minimap_player_x < minimap_x + minimap_width and 
        minimap_y <= minimap_player_y < minimap_y + minimap_height):
        screen.draw_char(minimap_player_x, 
                         minimap_player_y, 
                         '☺', 
                         Colors.BRIGHT_CYAN)

    # Draw "Map" text above minimap
    map_text = "Mini Map (M)"
    text_x = minimap_x + (minimap_width - len(map_text)) // 2
    screen.draw_string(text_x, minimap_y - 2, map_text, 
                       Colors.BRIGHT_BLACK)
    
def get_interaction_position(player_pos: List[int], 
                             direction: PlayerDirection
                             ) -> Tuple[int, int]:
    """Get the position in front of the player based on their direction"""
    dx, dy = 0, 0
    if direction == PlayerDirection.UP:
        dy = -1
    elif direction == PlayerDirection.DOWN:
        dy = 1
    elif direction == PlayerDirection.LEFT:
        dx = -1
    elif direction == PlayerDirection.RIGHT:
        dx = 1
    return (player_pos[0] + dx, player_pos[1] + dy)

def initialize_map_data() -> List[List[str]]:
    """Convert VILLAGE_MAP strings into a 2D list for easier access."""
    return [list(row) for row in VILLAGE_MAP]

def handle_collision(game_state: EnhancedGameState, x: int, y: int):
    """Handle collision with different map elements"""
    if 0 <= y < len(VILLAGE_MAP) and 0 <= x < len(VILLAGE_MAP[y]):
        terrain = VILLAGE_MAP[y][x]
        if terrain == 'H':
            game_state.set_status("Press F to enter house", 
                                  Colors.BRIGHT_YELLOW, 30)
        elif terrain == 'T':
            game_state.set_status("Use axe to cut tree", 
                                  Colors.BRIGHT_YELLOW, 30)
        elif terrain == '~':
            game_state.set_status("Can't swim in water!", 
                                  Colors.BRIGHT_BLUE, 30)
        elif terrain == 'm':
            game_state.set_status("Press F to enter mine", 
                                  Colors.BRIGHT_YELLOW, 30)
        elif terrain == 'p':
            game_state.set_status("Press F to enter portal", 
                                  Colors.BRIGHT_MAGENTA, 30)
        else:
            game_state.set_status("Can't walk there!", 
                                  Colors.BRIGHT_RED, 30)
    else:
        game_state.set_status("Can't leave the map!", 
                              Colors.BRIGHT_RED, 30)

def handle_tool_selection(game_state: EnhancedGameState, key: str):
    """Handle tool selection input"""
    tools = {
        '1': ToolType.AXE,
        '2': ToolType.HOE,
        '3': ToolType.SEEDS,
        '4': ToolType.WATERING_CAN,
        '5': ToolType.NONE
    }
    if key in tools:
        tool = tools[key]
        if game_state.select_tool(tool):
            if tool == ToolType.NONE:
                game_state.set_status("Tools unequipped", 
                                      Colors.BRIGHT_WHITE, 30)
            else:
                game_state.set_status(f"{tool.name.title()} equipped!", 
                                      Colors.BRIGHT_GREEN, 30)
        else:
            game_state.set_status(f"You don't have a {tool.name.lower()} yet!", 
                                  Colors.BRIGHT_RED, 30)

def handle_tool_use(game_state: EnhancedGameState):
    """Handle tool usage"""
    if game_state.current_tool == ToolType.NONE:
        game_state.set_status("Select a tool first! (1-4)", 
                              Colors.BRIGHT_YELLOW, 30)
        return False
        
    # Get interaction position
    interact_pos = get_interaction_position(game_state.player_pos, 
                                            game_state.player_direction)
    x, y = interact_pos
    
    # Check position validity
    if not (0 <= y < len(VILLAGE_MAP) and 0 <= x < len(VILLAGE_MAP[0])):
        game_state.set_status("Can't use tool here!", 
                              Colors.BRIGHT_RED, 30)
        return False

    # Check energy before proceeding
    if not game_state.use_energy(5):  # Using tools costs energy
        return False

    map_tile = VILLAGE_MAP[y][x]
    obj = game_state.get_object(x, y)

    try:
        # Handle tool usage based on tool type
        if game_state.current_tool == ToolType.AXE:
            if map_tile == 'T' or (obj and obj.tile_type == 'tree'):
                # Create tree object if it doesn't exist
                if not obj:
                    game_state.add_object(x, y, 'tree')
                    obj = game_state.get_object(x, y)

                # Damage tree
                obj.health = max(0, obj.health - 34)
                if obj.health <= 0:
                    # Tree has been cut down
                    wood_amount = random.randint(2, 4)
                    game_state.add_item('wood', wood_amount)
                    # Convert to stump
                    obj.tile_type = 'stump'
                    obj.regrowth_time = ((game_state.time_hours * 60) 
                                         + game_state.time_minutes + 60)
                    game_state.set_status(f"Got {wood_amount} wood!", 
                                          Colors.BRIGHT_GREEN, 30)
                else:
                    game_state.set_status(f"Tree health: {obj.health}%", 
                                          Colors.BRIGHT_YELLOW, 30)
                return True

        elif game_state.current_tool == ToolType.HOE:
            if map_tile == 'G' and not obj:  # Only till grass with no objects
                game_state.add_object(x, y, 'farm_plot')
                game_state.set_status("Created farm plot!", 
                                      Colors.BRIGHT_GREEN, 30)
                return True

        elif game_state.current_tool == ToolType.SEEDS:
            if obj and obj.tile_type == 'farm_plot':
                if game_state.inventory.get('seeds', 0) > 0:
                    game_state.remove_item('seeds', 1)
                    obj.tile_type = 'crops_seeds'
                    obj.growth_time = 0
                    game_state.set_status("Planted seeds!", 
                                          Colors.BRIGHT_GREEN, 30)
                    return True
                else:
                    game_state.set_status("No seeds!", 
                                          Colors.BRIGHT_RED, 30)
                    return False

        game_state.set_status("Can't use tool here!", 
                              Colors.BRIGHT_RED, 30)
        return False

    except Exception as e:
        logging.error(f"Error in handle_tool_use: {str(e)}")
        game_state.set_status("Tool use failed!", Colors.BRIGHT_RED, 30)
        return False

def handle_shop_interaction(game_state: EnhancedGameState) -> bool:
    """Handle interaction with shop, return True if interaction occurred"""
    # Get the position the player is facing
    interact_pos = get_interaction_position(game_state.player_pos, 
                                            game_state.player_direction)
    x, y = interact_pos
    
    # Check if position is valid and contains a shop
    if 0 <= y < len(VILLAGE_MAP) and 0 <= x < len(VILLAGE_MAP[0]):
        if VILLAGE_MAP[y][x] == 's':  # 's' is the shop tile
            # Check if player has wood to sell
            wood_amount = game_state.inventory.get('wood', 0)
            if wood_amount > 0:
                # Calculate money to add (5 gold per wood)
                money_earned = wood_amount * ItemType.get_base_price('wood')
                
                # Remove wood and add money
                game_state.inventory['wood'] = 0
                game_state.money += money_earned
                
                # Set status message
                game_state.set_status(
                    f"Sold {wood_amount} wood for ${money_earned}!",
                    Colors.BRIGHT_GREEN,
                    60
                )
                return True
            else:
                game_state.set_status("No wood to sell!", 
                                      Colors.BRIGHT_YELLOW, 30)
                return False
    return False

def handle_interaction(game_state: EnhancedGameState, key: str) -> bool:
    """Handle all interaction types"""
    if key not in ['f', 'F']:
        return False
        
    # Get the position the player is facing
    interact_pos = get_interaction_position(game_state.player_pos, 
                                            game_state.player_direction)
    x, y = interact_pos
    
    # Check if position is valid
    if not (0 <= y < len(VILLAGE_MAP) and 0 <= x < len(VILLAGE_MAP[0])):
        return False
        
    # Get the tile type
    tile = VILLAGE_MAP[y][x]
    
    if tile == 'H':
        # Handle house interaction
        game_state.energy = game_state.max_energy
        game_state.time_hours += 8
        game_state.time_minutes = 0
        game_state.day += 1
        game_state.set_status("Got a good night's sleep! Energy restored.", 
                              Colors.BRIGHT_GREEN, 60)
        return True
        
    elif tile == 's':
        # Handle shop interaction
        return handle_shop_interaction(game_state)
        
    # Check for other interactions (crops, etc.)
    obj = game_state.get_object(x, y)
    if obj and obj.can_interact():
        if obj.tile_type == 'crops_ready':
            # Handle crop harvesting
            if obj.harvest():
                game_state.set_status("Harvested crops!", 
                                      Colors.BRIGHT_GREEN, 30)
                return True
    
    return False
           
def handle_house_interaction(game_state: EnhancedGameState) -> bool:
    """Handle interaction with house, return True if interaction occurred"""
    # Get the position the player is facing
    interact_pos = get_interaction_position(game_state.player_pos, 
                                            game_state.player_direction)
    x, y = interact_pos
    
    # Check if position is valid and contains a house
    if 0 <= y < len(VILLAGE_MAP) and 0 <= x < len(VILLAGE_MAP[0]):
        if VILLAGE_MAP[y][x] == 'H':
            # Restore energy to max
            game_state.energy = game_state.max_energy
            
            # Reset time to 6 AM
            game_state.time_hours = 6
            game_state.time_minutes = 0
            
            # Increment day
            game_state.day += 1
            
            # Set status message
            game_state.set_status(
                "Got a good night's sleep! Energy restored.", 
                Colors.BRIGHT_GREEN, 60)
            return True
    return False
            
def main_game_loop():
    """Main game loop with menu system and state management"""
    game_state = EnhancedGameState()
    ui_panel = UIPanel()
    main_menu = MainMenu()
    pause_menu = PauseMenu()
    current_state = GameState.MAIN_MENU
    
    running = True
    last_frame_time = time.time()
    
    while running:
        try:
            current_time = time.time()
            if (current_time - last_frame_time 
                < frame_controller.frame_time):
                time.sleep(
                    frame_controller.frame_time - current_time 
                    + last_frame_time)
            last_frame_time = current_time
            
            # Clear screen buffer
            screen_buffer.clear()
            
            if current_state == GameState.MAIN_MENU:
                # Draw menu
                main_menu.draw(screen_buffer)
                screen_buffer.render()
                
                # Handle input
                key = input_handler.getch()
                if key:
                    new_state = main_menu.handle_input(key)
                    if new_state:
                        if new_state == GameState.QUIT:
                            running = False
                        elif new_state == GameState.PLAYING:
                            game_state = EnhancedGameState()
                            game_state.set_status("Welcome to Farm Quest! Use WASD to move.", 
                                                  Colors.BRIGHT_GREEN, 120)
                            current_state = new_state
                        else:
                            current_state = new_state
            
            elif current_state == GameState.PLAYING:
                key = input_handler.getch()
                if key:
                    if key == chr(27):  # ESC
                        current_state = GameState.PAUSED
                    elif key in ['f', 'F']:
                        # Try to interact with structures/objects
                        handle_interaction(game_state, key)
                    else:
                        handle_gameplay_input(game_state, key.lower())
                
                # Update game state
                game_state.update_status()
                for obj in list(game_state.objects.values()):
                    obj.update(game_state)
                
                # Draw game screen
                draw_border(screen_buffer)
                screen_buffer.draw_string(
                    (MAIN_AREA_WIDTH - len("Home Village")) // 2,
                    1,
                    "Home Villagge",
                    Colors.BRIGHT_GREEN
                )
                draw_village_map(screen_buffer, game_state)
                draw_status_line(screen_buffer, game_state)
                ui_panel.draw(screen_buffer, game_state)
                screen_buffer.render()
            
            elif current_state == GameState.PAUSED:
                pause_menu.draw(screen_buffer)
                screen_buffer.render()
                
                key = input_handler.getch()
                if key:
                    new_state = pause_menu.handle_input(key)
                    if new_state:
                        if new_state == GameState.QUIT:
                            running = False
                        else:
                            current_state = new_state
            
        except Exception as e:
            logging.error(f"Error in game loop: {str(e)}")
            if game_state:
                game_state.set_status(f"Error: {str(e)}", Colors.BRIGHT_RED, 60)
            continue

    return running

if __name__ == "__main__":
    try:
        clear_screen()
        main_game_loop()
    finally:
        cleanup()
        clear_screen()
        print("Thanks for playing Farm Quest!")