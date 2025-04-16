# -*- coding: utf-8 -*-

import curses
import time
import math
import sys
import argparse
import json
from curses import wrapper
import random

class AnimationEffect:
    def __init__(self, name,
                 wave_speed=2.0,
                 wave_scale=2.0,
                 pulse_speed=1.5,
                 pulse_scale=0.3,
                 color_speed=2.0):
        self.name = name
        self.wave_speed = wave_speed
        self.wave_scale = wave_scale
        self.pulse_speed = pulse_speed
        self.pulse_scale = pulse_scale
        self.color_speed = color_speed

    def apply(self, char_index, time, position_factor):
        if self.name == "wave":
            return (
                math.sin(time * self.wave_speed + char_index * 0.3 + position_factor * math.pi) * self.wave_scale,
                0
            )
        elif self.name == "bounce":
            return (
                abs(math.sin(time * self.wave_speed + char_index * 0.2)) * self.wave_scale,
                0
            )
        elif self.name == "spiral":
            angle = time * self.wave_speed + char_index * 0.2
            return (
                math.sin(angle) * self.wave_scale,
                math.cos(angle) * self.wave_scale
            )
        elif self.name == "shake":
            return (
                random.uniform(-1, 1) * self.wave_scale * 0.5,
                random.uniform(-1, 1) * self.wave_scale * 0.5
            )
        return (0, 0)

class Language:
    def __init__(self, text, color_start, position_factor, effect):
        self.text = text
        self.color_start = color_start
        self.position_factor = position_factor
        self.effect = effect

class TextAnimator:
    def __init__(self, languages, fps=60, color_scheme="rainbow", save_to_file=None):
        self.languages = languages
        self.frame_delay = 1.0 / fps
        self.color_scheme = color_scheme
        self.save_to_file = save_to_file
        self.recorded_frames = [] if save_to_file else None

    def setup_colors(self, stdscr):
        curses.start_color()
        if self.color_scheme == "rainbow":
            colors = [
                curses.COLOR_RED,
                curses.COLOR_YELLOW,
                curses.COLOR_GREEN,
                curses.COLOR_CYAN,
                curses.COLOR_BLUE,
                curses.COLOR_MAGENTA
            ]
        elif self.color_scheme == "monochrome":
            colors = [curses.COLOR_WHITE] * 6
        elif self.color_scheme == "matrix":
            colors = [curses.COLOR_GREEN] * 6
        
        for i, fg in enumerate(colors):
            curses.init_pair(i + 1, fg, curses.COLOR_BLACK)

    def save_frame(self, frame_data):
        if self.recorded_frames is not None:
            self.recorded_frames.append(frame_data)

    def save_animation(self):
        if self.save_to_file and self.recorded_frames:
            with open(self.save_to_file, 'w') as f:
                json.dump(self.recorded_frames, f)

    def run(self, stdscr):
        self.setup_colors(stdscr)
        curses.curs_set(0)
        stdscr.addstr(0, 0, "")
        
        start_time = time.time()
        
        while True:
            current_time = time.time()
            animation_time = current_time - start_time
            
            height, width = stdscr.getmaxyx()
            stdscr.clear()
            
            frame_data = {"time": animation_time, "texts": []}
            
            for lang in self.languages:
                y_pos = int(height * lang.position_factor)
                x_pos = width // 2 - len(lang.text) // 2
                
                text_data = {"text": lang.text, "positions": []}
                
                for i, char in enumerate(lang.text):
                    offset_y, offset_x = lang.effect.apply(i, animation_time, lang.position_factor)
                    
                    final_y = int(y_pos + offset_y)
                    final_x = int(x_pos + i + offset_x)
                    
                    color_idx = ((int(animation_time * lang.effect.color_speed) + i + lang.color_start) % 3) + lang.color_start % 3 + 1
                    
                    if 0 <= final_y < height - 1 and 0 <= final_x < width - len(char):
                        try:
                            char_bytes = char.encode('utf-8')
                            decoded_char = char_bytes.decode('utf-8')
                            stdscr.addstr(final_y, final_x, decoded_char, curses.color_pair(color_idx) | curses.A_BOLD)
                            text_data["positions"].append({"char": char, "x": final_x, "y": final_y, "color": color_idx})
                        except (curses.error, UnicodeEncodeError, UnicodeDecodeError):
                            pass
                
                frame_data["texts"].append(text_data)
            
            self.save_frame(frame_data)
            stdscr.refresh()
            time.sleep(self.frame_delay)
            
            stdscr.nodelay(1)
            if stdscr.getch() != -1:
                break
        
        self.save_animation()

def main():
    parser = argparse.ArgumentParser(description='Animated Text Display')
    parser.add_argument('--text', '-t', nargs='+', help='Custom text to display (can be multiple)')
    parser.add_argument('--effect', '-e', choices=['wave', 'bounce', 'spiral', 'shake'], default='wave',
                       help='Animation effect to apply')
    parser.add_argument('--fps', type=int, default=60, help='Frames per second')
    parser.add_argument('--colors', '-c', choices=['rainbow', 'monochrome', 'matrix'], default='rainbow',
                       help='Color scheme')
    parser.add_argument('--save', '-s', help='Save animation to file')
    args = parser.parse_args()

    # Default texts if none provided
    if not args.text:
        texts = [
            ("Hello, World!", 0, 0.2),
            ("Bonjour, le Monde!", 1, 0.35),
            ("안녕하세요, 세상!", 2, 0.5),
            ("¡Hola, Mundo!", 3, 0.65),
            ("こんにちは、世界！", 4, 0.8)
        ]
    else:
        spacing = 1.0 / (len(args.text) + 1)
        texts = [(text, i, spacing * (i + 1)) for i, text in enumerate(args.text)]

    effect = AnimationEffect(args.effect)
    languages = [Language(text, color, pos, effect) for text, color, pos in texts]
    
    animator = TextAnimator(
        languages=languages,
        fps=args.fps,
        color_scheme=args.colors,
        save_to_file=args.save
    )
    
    wrapper(animator.run)

if __name__ == "__main__":
    # Force UTF-8 encoding for the terminal
    import locale
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    locale.setlocale(locale.LC_ALL, '')
    main()
