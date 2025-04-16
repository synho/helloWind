# -*- coding: utf-8 -*-

import pygame
import sys
import math
import random
import numpy as np
from pygame import gfxdraw
import argparse
import time
import os

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]
        self.size = random.uniform(2, 4)

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= self.decay
        self.velocity[1] += 0.1  # Gravity
        return self.life > 0

    def draw(self, screen):
        alpha = int(255 * self.life)
        color = self.color + (alpha,)
        gfxdraw.filled_circle(screen, int(self.x), int(self.y), int(self.size), color)

class Text:
    def __init__(self, text, color, size=40):
        self.text = text
        self.base_color = color
        self.particles = []
        self.size = size
        self.position = [0, 0]
        self.target = [0, 0]
        self.velocity = [0, 0]
        self.angle = 0
        self.scale = 1.0
        self.char_widths = []  # Store individual character widths
        
    def update(self, time):
        # Update position with smooth movement
        dx = (self.target[0] - self.position[0]) * 0.1
        dy = (self.target[1] - self.position[1]) * 0.1
        self.position[0] += dx
        self.position[1] += dy
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Add new particles occasionally
        if random.random() < 0.3:
            total_width = sum(self.char_widths) if self.char_widths else self.size * len(self.text)
            x = self.position[0] + random.uniform(0, total_width)
            y = self.position[1] + random.uniform(-self.size/2, self.size/2)
            self.particles.append(Particle(x, y, self.base_color))

    def calculate_char_widths(self, font):
        self.char_widths = []
        for char in self.text:
            # Get the width of each character
            char_surface = font.render(char, True, self.base_color)
            self.char_widths.append(char_surface.get_width())

    def draw(self, screen, font, time):
        if not self.char_widths:
            self.calculate_char_widths(font)

        # Create shimmering effect
        color = list(self.base_color)
        shimmer = math.sin(time * 3) * 0.2 + 0.8
        color = [min(255, c * shimmer) for c in color]
        
        # Apply wave effect
        wave_height = 10
        wave_length = 0.1
        wave_speed = 3
        
        # Calculate total width for centering
        total_width = sum(self.char_widths)
        current_x = self.position[0]
        
        for i, char in enumerate(self.text):
            char_surface = font.render(char, True, color)
            shadow_surface = font.render(char, True, (0, 0, 0))
            
            # Calculate position for this character
            x = current_x
            y = self.position[1] + math.sin(time * wave_speed + i * wave_length) * wave_height
            
            # Draw shadow
            screen.blit(shadow_surface, (x + 2, y + 2))
            # Draw text
            screen.blit(char_surface, (x, y))
            
            # Move to next character position
            current_x += self.char_widths[i]
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

class VisualAnimator:
    def __init__(self, width=1200, height=800):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Visual Hello World")
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height
        self.texts = []
        
        # Try to get a CJK-compatible font
        system_font = get_system_font()
        if system_font:
            try:
                self.font = pygame.font.Font(system_font, 48)
            except:
                # If loading the system font fails, fall back to default
                self.font = pygame.font.SysFont('Arial', 48)
        else:
            # If no CJK font is found, try to use a system font that might support CJK
            self.font = pygame.font.SysFont('Arial', 48)
        
        self.background_color = (10, 10, 20)
        self.start_time = time.time()

    def add_text(self, text, color):
        new_text = Text(text, color)
        # Calculate initial position
        new_text.calculate_char_widths(self.font)
        total_width = sum(new_text.char_widths)
        new_text.position[0] = self.width / 2 - total_width / 2
        self.texts.append(new_text)
        return new_text

    def run(self):
        running = True
        while running:
            current_time = time.time() - self.start_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Clear screen with fade effect
            self.screen.fill(self.background_color)
            
            # Update and draw all text objects
            for i, text in enumerate(self.texts):
                # Calculate target position
                target_y = self.height * (i + 1) / (len(self.texts) + 1)
                total_width = sum(text.char_widths)
                text.target = [self.width / 2 - total_width / 2, target_y]
                
                text.update(current_time)
                text.draw(self.screen, self.font, current_time)
            
            # Draw stars in background
            for _ in range(5):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                size = random.randint(1, 3)
                alpha = random.randint(50, 200)
                gfxdraw.filled_circle(self.screen, x, y, size, (255, 255, 255, alpha))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

def get_system_font():
    # Try different system fonts that support CJK characters
    font_names = [
        "NotoSansCJK-Regular.ttc",
        "NotoSansJP-Regular.otf",
        "NanumGothic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"
    ]
    
    for font_name in font_names:
        if os.path.exists(font_name):
            return font_name
    
    # If no specific font is found, try system default fonts
    try:
        import tkinter as tk
        root = tk.Tk()
        system_fonts = [f.name for f in pygame.font.get_fonts() if 'noto' in f.lower() or 'cjk' in f.lower()]
        root.destroy()
        if system_fonts:
            return system_fonts[0]
    except:
        pass
    
    return None

def main():
    parser = argparse.ArgumentParser(description='Visual Text Animation')
    parser.add_argument('--text', '-t', nargs='+', help='Custom text to display (can be multiple)')
    args = parser.parse_args()

    animator = VisualAnimator()

    if args.text:
        colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255)   # Purple
        ]
        for i, text in enumerate(args.text):
            animator.add_text(text, colors[i % len(colors)])
    else:
        # Default multilingual text
        animator.add_text("Hello, World!", (255, 100, 100))
        animator.add_text("Bonjour, le Monde!", (100, 255, 100))
        animator.add_text("안녕하세요, 세상!", (100, 100, 255))
        animator.add_text("¡Hola, Mundo!", (255, 255, 100))
        animator.add_text("こんにちは、世界！", (255, 100, 255))

    animator.run()

if __name__ == "__main__":
    main()
