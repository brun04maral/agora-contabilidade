#!/usr/bin/env python3
"""
Script to create apple-touch-icon.png from favicon.svg
Requires: pip install pillow cairosvg
"""
import os

try:
    from cairosvg import svg2png

    svg_path = '/home/zumine/amp/docker/agora-contabilidade/media/logos/favicon.svg'
    png_path = '/home/zumine/amp/docker/agora-contabilidade/media/logos/apple-touch-icon.png'

    svg2png(url=svg_path, write_to=png_path, output_width=180, output_height=180)
    print(f"✓ Created {png_path}")

except ImportError:
    print("✗ cairosvg not installed. Please run:")
    print("  pip install cairosvg pillow")
    print("  Then run this script again")
    exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)
