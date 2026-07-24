#!/usr/bin/env bash
set -euo pipefail

TARGET_BIN="$HOME/.local/bin/PathfinderBuildTool"
DESKTOP_FILE="$HOME/.local/share/applications/PathfinderBuildTool.desktop"
ICON_PNG="$HOME/.local/share/icons/PathfinderBuildTool.png"
ICON_ICO="$HOME/.local/share/icons/PathfinderBuildTool.ico"

remove_if_exists() {
  local path="$1"
  if [[ -e "$path" ]]; then
    rm -f "$path"
    echo "Removed: $path"
  else
    echo "Not found (skipped): $path"
  fi
}

remove_if_exists "$TARGET_BIN"
remove_if_exists "$DESKTOP_FILE"
remove_if_exists "$ICON_PNG"
remove_if_exists "$ICON_ICO"

echo "Uninstall complete."
