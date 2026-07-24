#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_BIN="${1:-$SCRIPT_DIR/PathfinderBuildTool}"
FALLBACK_ICON="applications-games"

if [[ ! -f "$SOURCE_BIN" ]]; then
  echo "Error: executable not found at '$SOURCE_BIN'."
  echo "Usage: ./install.sh [path-to-PathfinderBuildTool]"
  exit 1
fi

BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"

mkdir -p "$BIN_DIR" "$APP_DIR" "$ICON_DIR"

TARGET_BIN="$BIN_DIR/PathfinderBuildTool"
install -m 755 "$SOURCE_BIN" "$TARGET_BIN"
echo "Installed executable: $TARGET_BIN"

ICON_ENTRY="$FALLBACK_ICON"
if [[ -f "$SCRIPT_DIR/data/logo.png" ]]; then
  ICON_TARGET="$ICON_DIR/PathfinderBuildTool.png"
  install -m 644 "$SCRIPT_DIR/data/logo.png" "$ICON_TARGET"
  ICON_ENTRY="$ICON_TARGET"
  echo "Installed icon: $ICON_TARGET"
elif [[ -f "$SCRIPT_DIR/data/logo.ico" ]]; then
  ICON_TARGET="$ICON_DIR/PathfinderBuildTool.ico"
  install -m 644 "$SCRIPT_DIR/data/logo.ico" "$ICON_TARGET"
  ICON_ENTRY="$ICON_TARGET"
  echo "Installed icon: $ICON_TARGET"
else
  echo "No logo file found beside installer; using fallback desktop icon."
fi

DESKTOP_FILE="$APP_DIR/PathfinderBuildTool.desktop"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Pathfinder Build Tool
Exec=$TARGET_BIN
Terminal=false
Categories=Game;Utility;
Icon=$ICON_ENTRY
EOF

chmod 644 "$DESKTOP_FILE"

echo "Installed desktop entry: $DESKTOP_FILE"
echo "Installation complete. You can launch Pathfinder Build Tool from your application menu."
