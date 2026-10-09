#!/bin/bash
# Applies the preset stored in this folder (mate.dconf, brisk.dconf, gnome.dconf, gtk.css).
set -e
W="$(cd "$(dirname "$0")" && pwd)"
D="$HOME/.local/bin/dconf"
"$D" reset -f /org/mate/
"$D" load /org/mate/ < "$W/mate.dconf"
"$D" reset -f /com/solus-project/
"$D" load /com/solus-project/ < "$W/brisk.dconf"
"$D" reset -f /org/gnome/desktop/interface/
[ -f "$W/gnome.dconf" ] && "$D" load /org/gnome/desktop/interface/ < "$W/gnome.dconf"
mkdir -p "$HOME/.config/gtk-3.0"; cp "$W/gtk.css" "$HOME/.config/gtk-3.0/gtk.css"
pkill -x brisk-menu || true
(setsid mate-panel --replace >/dev/null 2>&1 &)
# The running panel deletes some items while the config is loading: load it again once the panel has restarted
sleep 3
"$D" load /org/mate/ < "$W/mate.dconf"
(setsid mate-panel --replace >/dev/null 2>&1 &)
echo "Preset $(basename "$W") applied."
