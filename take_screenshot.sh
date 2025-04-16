#!/bin/bash
# Start the animation
python3 visual_hello.py &
# Wait for the window to be fully rendered
sleep 3
# Take the screenshot
scrot -u 'docs/demo.png'
# Kill the animation
pkill -f "python3 visual_hello.py"
