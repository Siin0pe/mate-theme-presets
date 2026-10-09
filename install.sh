#!/bin/bash
# Installs the Windows / macOS / Ubuntu theme presets for MATE, without root.
# Usage: ./install.sh [windows|macos|ubuntu]   (optional: preset to apply at the end)
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
P="$HERE/payload"
R="$HOME/.theme-backup"
BIN="$HOME/.local/bin"
D="$BIN/dconf"

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m/!\\\033[0m %s\n' "$*"; }

# ---------- Checks ----------
[ -d "$P" ] || { echo "payload/ not found: run this script from the extracted project folder."; exit 1; }
case "$XDG_CURRENT_DESKTOP" in
  *MATE*) ;;
  *) warn "Detected desktop: '${XDG_CURRENT_DESKTOP:-unknown}'. These presets are made for MATE."
     read -r -p "Continue anyway? [y/N] " a; [[ "$a" =~ ^[yY] ]] || exit 1 ;;
esac
command -v python3 >/dev/null || { echo "python3 is required."; exit 1; }

mkdir -p "$BIN" "$R" "$HOME/.themes" "$HOME/.icons" "$HOME/.local/share/fonts"

# ---------- Tools ----------
say "Installing tools (dconf, preset, theme-picker) to $BIN"
cp "$P/bin/dconf" "$P/bin/preset" "$P/bin/theme-picker" "$BIN/"
chmod +x "$BIN/dconf" "$BIN/preset" "$BIN/theme-picker"
"$D" help >/dev/null 2>&1 || { echo "The bundled dconf binary does not run on this machine (is libdconf1 missing?)."; exit 1; }

# ---------- Back up the current look (only once) ----------
if [ -e "$R/original/mate.dconf" ]; then
  say "Existing backup found in $R/original (kept as is)"
else
  B="$R/original-$(date +%Y%m%d-%H%M%S)"
  say "Backing up your current desktop settings to $B"
  mkdir -p "$B"
  "$D" dump /org/mate/ > "$B/mate.dconf"
  "$D" dump /com/solus-project/ > "$B/brisk.dconf"
  "$D" dump /org/gnome/desktop/interface/ > "$B/gnome.dconf"
  [ -f "$HOME/.config/dconf/user" ] && cp "$HOME/.config/dconf/user" "$B/dconf-user.raw"
  for d in gtk-3.0 gtk-4.0; do [ -d "$HOME/.config/$d" ] && cp -r "$HOME/.config/$d" "$B/$d"; done
  [ -f "$HOME/.gtkrc-2.0" ] && cp "$HOME/.gtkrc-2.0" "$B/"
  cp "$P/scripts/restore.sh" "$B/restore.sh"; chmod +x "$B/restore.sh"
  ln -sfn "$B" "$R/original"
fi

# ---------- Themes, icons, fonts ----------
say "Installing GTK themes to ~/.themes"
cp -a "$P/themes/." "$HOME/.themes/"
say "Installing icons and cursors to ~/.icons (this can take a minute)"
cp -a "$P/icons/." "$HOME/.icons/"
for t in "$P"/icons/*/; do
  t=$(basename "$t"); [ -f "$HOME/.icons/$t/index.theme" ] && gtk-update-icon-cache -f -q "$HOME/.icons/$t" 2>/dev/null || true
done
say "Installing fonts to ~/.local/share/fonts"
cp -a "$P/fonts/." "$HOME/.local/share/fonts/"
fc-cache -f "$HOME/.local/share/fonts" >/dev/null 2>&1 || true

say "Installing the macOS menu icon to ~/.local/share/icons/hicolor"
H="$HOME/.local/share/icons/hicolor"
mkdir -p "$H/scalable/apps"
cp "$P/hicolor/menu-emoji.svg" "$H/scalable/apps/"
[ -f "$H/index.theme" ] || cp /usr/share/icons/hicolor/index.theme "$H/"
gtk-update-icon-cache -f -q "$H" 2>/dev/null || true

# ---------- Presets ----------
say "Installing wallpapers, dock launchers and the preset generator to $R"
mkdir -p "$R/wallpapers" "$R/launchers"
cp "$P/wallpapers/"* "$R/wallpapers/"
cp "$P/launchers/"*.desktop "$R/launchers/"
cp "$P/scripts/build_presets.py" "$P/scripts/apply.sh" "$R/"
chmod +x "$R/apply.sh"
say "Generating the presets from your own configuration"
python3 "$R/build_presets.py"

# ---------- Desktop launcher ----------
DESK=$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")
mkdir -p "$DESK"
F="$DESK/Change Theme.desktop"
cat > "$F" <<EOF
[Desktop Entry]
Type=Application
Name=Change Theme
Comment=Switch between Default, Windows, macOS and Ubuntu looks
Exec=$BIN/theme-picker
Icon=preferences-desktop-theme
Terminal=false
EOF
chmod +x "$F"
gio set "$F" metadata::trusted true 2>/dev/null || true
say "Added a “Change Theme” launcher to your desktop"

# ---------- Apply ----------
choice="$1"
if [ -z "$choice" ]; then
  echo
  read -r -p "Apply a preset now? [windows/macos/ubuntu/no] " choice
fi
case "$choice" in
  windows|macos|ubuntu) say "Applying the $choice preset"; "$BIN/preset" "$choice" ;;
  *) echo "Nothing applied. Double-click “Change Theme” on your desktop whenever you like." ;;
esac

echo
say "Installation complete."
echo "    Switch looks:        “Change Theme” on the desktop, or 'preset windows|macos|ubuntu|original'"
echo "    Back to your theme:  preset original"
echo "    Remove everything:   ./uninstall.sh"
