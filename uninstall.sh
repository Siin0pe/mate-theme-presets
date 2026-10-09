#!/bin/bash
# Restores the original theme and removes everything install.sh added.
HERE="$(cd "$(dirname "$0")" && pwd)"
P="$HERE/payload"
R="$HOME/.theme-backup"
BIN="$HOME/.local/bin"

read -r -p "Restore your original theme and remove the installed presets? [y/N] " a
[[ "$a" =~ ^[yY] ]] || exit 0

if [ -x "$R/original/restore.sh" ]; then
  "$R/original/restore.sh"
else
  echo "No original backup found: leaving the current theme as it is."
fi

# Only remove what this project installed (based on the contents of payload/)
for t in "$P"/themes/*/;  do rm -rf "$HOME/.themes/$(basename "$t")"; done
for t in "$P"/icons/*/ "$P"/icons/.[!.]*/; do [ -d "$t" ] && rm -rf "$HOME/.icons/$(basename "$t")"; done
for f in "$P"/fonts/*/;   do rm -rf "$HOME/.local/share/fonts/$(basename "$f")"; done
fc-cache -f "$HOME/.local/share/fonts" >/dev/null 2>&1
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/menu-emoji.svg"
rm -f "$BIN/preset" "$BIN/theme-picker"
DESK=$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")
rm -f "$DESK/Change Theme.desktop" "$DESK/Changer de thème.desktop"   # current name and the earlier French name

echo
echo "Presets removed. Deliberately kept:"
echo "  - $R (your original backup): delete it manually if you no longer need it"
echo "  - $BIN/dconf (used by the backup's restore script)"
