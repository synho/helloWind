# -*- coding: utf-8 -*-

import curses
import time
import math
from curses import wrapper
import sys

class Language:
    def __init__(self, text, color_start, position_factor):
        self.text = text
        self.color_start = color_start  # Starting color index
        self.position_factor = position_factor  # Vertical position factor (0 to 1)

def setup_colors():
    # Initialize color pairs
    colors = [
        curses.COLOR_RED,
        curses.COLOR_YELLOW,
        curses.COLOR_GREEN,
        curses.COLOR_CYAN,
        curses.COLOR_BLUE,
        curses.COLOR_MAGENTA
    ]
    
    for i, fg in enumerate(colors):
        curses.init_pair(i + 1, fg, curses.COLOR_BLACK)

def main(stdscr):
    # Set up terminal for UTF-8
    curses.start_color()
    setup_colors()
    curses.curs_set(0)  # Hide cursor
    
    # Define languages with their positions and colors
    languages = [
        Language("Hello, World!", 0, 0.2),          # English - top
        Language("Bonjour, le Monde!", 1, 0.35),    # French - upper middle
        Language("안녕하세요, 세상!", 2, 0.5),      # Korean - center
        Language("¡Hola, Mundo!", 3, 0.65),         # Spanish - lower middle
        Language("こんにちは、世界！", 4, 0.8)      # Japanese - bottom
    ]
    
    # Enable extended ASCII and UTF-8 mode
    stdscr.addstr(0, 0, "")  # Initialize screen
    
    start_time = time.time()
    
    while True:
        current_time = time.time()
        animation_time = current_time - start_time
        
        # Get terminal dimensions
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        
        # Draw each language
        for lang in languages:
            # Calculate base position
            y_pos = int(height * lang.position_factor)
            x_pos = width // 2 - len(lang.text) // 2
            
            # Apply wave and pulse effects
            for i, char in enumerate(lang.text):
                # Wave effect - unique for each language
                wave = math.sin(animation_time * 2 + i * 0.3 + lang.position_factor * math.pi) * 2
                
                # Pulse effect - unique for each language
                pulse = math.sin(animation_time * 1.5 + lang.position_factor * math.pi) * 0.3 + 1
                
                # Calculate final position
                final_y = int(y_pos + wave)
                final_x = int(x_pos + i * pulse)
                
                # Calculate color (cycling through 3 colors for each language)
                color_idx = ((int(animation_time * 2) + i + lang.color_start) % 3) + lang.color_start % 3 + 1
                
                # Draw character with error handling
                if 0 <= final_y < height - 1 and 0 <= final_x < width - len(char):
                    try:
                        # Convert character to bytes and back to ensure proper encoding
                        char_bytes = char.encode('utf-8')
                        decoded_char = char_bytes.decode('utf-8')
                        stdscr.addstr(final_y, final_x, decoded_char, curses.color_pair(color_idx) | curses.A_BOLD)
                    except (curses.error, UnicodeEncodeError, UnicodeDecodeError):
                        pass
        
        stdscr.refresh()
        time.sleep(0.016)  # ~60 FPS
        
        # Check for key press to exit
        stdscr.nodelay(1)
        if stdscr.getch() != -1:
            break

if __name__ == "__main__":
    # Force UTF-8 encoding for the terminal
    import locale
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    locale.setlocale(locale.LC_ALL, '')
    code = locale.getpreferredencoding()
    wrapper(main)
