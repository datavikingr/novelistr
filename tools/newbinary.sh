#!/usr/bin/env bash

# Run this when I've updated the code inside novelistr.py
# This builds a new standalone binary.
# It outputs the binary to dist/novelistr

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$ROOT_DIR"

pyinstaller --onefile --noconfirm --windowed \
  --icon=assets/icon_32x32.png \
  --add-data "assets:assets" \
  --hidden-import=customtkinter \
  novelistr.py