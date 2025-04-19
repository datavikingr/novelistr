#!/usr/bin/env bash

build_binary_from_pyinstaller() {
  if [[ -z "$VIRTUAL_ENV" ]]; then
    source .venv/bin/activate
  fi

  pyinstaller --onefile --noconfirm --windowed \
    --icon=assets/icon_256x256.png \
    --add-data "assets:assets" \
    --hidden-import=customtkinter \
    novelistr.py

  if [[ -n "$VIRTUAL_ENV" ]]; then
    deactivate
  fi

  rm -rf build/ *.spec
}

# Only run this function if the script is executed directly,
# NOT if it is being sourced by another script.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  build_binary_from_pyinstaller
fi