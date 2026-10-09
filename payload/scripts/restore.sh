#!/bin/bash
# Restores the original MATE look backed up in this folder.
set -e
B="$(cd "$(dirname "$0")" && pwd)"
D="$HOME/.local/bin/dconf"
"$D" reset -f /org/mate/
"$D" load /org/mate/ < "$B/mate.dconf"
"$D" reset -f /com/solus-project/
[ -s "$B/brisk.dconf" ] && "$D" load /com/solus-project/ < "$B/brisk.dconf"
"$D" reset -f /org/gnome/desktop/interface/
[ -s "$B/gnome.dconf" ] && "$D" load /org/gnome/desktop/interface/ < "$B/gnome.dconf"
for d in gtk-3.0 gtk-4.0; do
  rm -rf "$HOME/.config/$d"
  [ -d "$B/$d" ] && cp -r "$B/$d" "$HOME/.config/$d"
done
rm -f "$HOME/.gtkrc-2.0"; [ -f "$B/.gtkrc-2.0" ] && cp "$B/.gtkrc-2.0" "$HOME/"
# Restart the panel so it re-reads its configuration
(setsid mate-panel --replace >/dev/null 2>&1 &)
# The running panel deletes some items while the config is loading: load it again once the panel has restarted
sleep 3
"$D" load /org/mate/ < "$B/mate.dconf"
(setsid mate-panel --replace >/dev/null 2>&1 &)
echo "Original theme restored."
