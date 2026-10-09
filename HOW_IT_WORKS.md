# How It Works

This document explains how a stock MATE desktop on a locked-down lab machine was turned into Windows, macOS and Ubuntu look-alikes **without administrator rights**. It also covers the problems hit along the way and how each was solved, since that is where most of the useful lessons are.

## Contents

0. [Starting point](#0-starting-point)
1. [Where a Linux desktop gets its look](#1-where-a-linux-desktop-gets-its-look)
2. [Getting tools without root](#2-getting-tools-without-root-apt-get-download--dpkg-deb--x)
3. [The themes](#3-the-themes)
4. [dconf: MATE's settings database](#4-dconf-mates-settings-database)
5. [The preset generator](#5-the-preset-generator)
6. [CSS: the finishing touches](#6-css-the-finishing-touches)
7. [Terminals](#7-terminals)
8. [Dark mode everywhere](#8-dark-mode-everywhere)
9. [Pitfalls and how they were solved](#9-pitfalls-and-how-they-were-solved)
10. [Files after installation](#10-files-after-installation)
11. [Going further](#11-going-further)

---

## 0. Starting point

The environment:
- **Debian 13 with MATE** (a fork of GNOME 2) on X11, 1920×1080 display;
- a student account **without `sudo`**;
- a **home directory on NFS**, so everything in `~` follows the user from machine to machine;
- internet access through a proxy.

Already installed and useful: **Brisk Menu** (a start menu with search), the **murrine** GTK engine, the compositor built into the **Marco** window manager (transparency, shadows), and `zenity` for simple dialog windows.

The constraint is that we can only write **inside the home directory**. Everything below follows from that.

---

## 1. Where a Linux desktop gets its look

A GTK/MATE desktop is made of two things:

1. **files**: themes, icons, fonts;
2. **configuration**: which theme to use, where the panels are, which font, and so on.

For both, the system looks in the user's home directory **before** the system-wide locations:

| What | System location (read-only for us) | Per-user location (writable) |
|---|---|---|
| GTK themes and window decorations | `/usr/share/themes` | `~/.themes` |
| Icons and cursors | `/usr/share/icons` | `~/.icons` (or `~/.local/share/icons`) |
| Fonts | `/usr/share/fonts` | `~/.local/share/fonts` |
| Settings | schema defaults | the **dconf** database, `~/.config/dconf/user` |
| CSS overrides | — | `~/.config/gtk-3.0/gtk.css` |

So the whole approach is: **drop files into those folders and change settings in dconf.** No root needed.

### What a “theme” is
A theme folder such as `WhiteSur-Dark/` contains:
- `gtk-3.0/gtk.css`: styles for GTK3 apps (buttons, menus, entries…);
- `gtk-2.0/`: the same for older GTK2 apps;
- `metacity-1/`: **window decorations** (title bar, close/minimise buttons). Marco, MATE's window manager, reads the Metacity theme format. Without this folder, a theme only changes what is inside windows.

An icon theme (`Fluent-dark/`) is a tree of `size/category/name.svg` files, described by an `index.theme` and indexed by an `icon-theme.cache` for fast lookups.

---

## 2. Getting tools without root: `apt-get download` + `dpkg-deb -x`

Some tools were missing: `dconf` (to export and import settings), `sassc` (to compile a theme from SCSS) and `rsvg-convert` (to build cursors).

`apt install` needs root, but:

```bash
apt-get download dconf-cli          # only downloads the .deb, no root needed
dpkg-deb -x dconf-cli_*.deb ./dconf # unpacks it like an archive
cp ./dconf/usr/bin/dconf ~/.local/bin/
```

A `.deb` is just an archive, so we take the binary out and put it in `~/.local/bin`. This works as long as the **libraries** it needs are already installed (here `libdconf1`, which MATE itself uses). When a library is missing, it can be extracted too and pointed to with `LD_LIBRARY_PATH`:

```bash
# sassc needs libsass1, which is missing: extract both and add a small wrapper
printf '#!/bin/sh\nLD_LIBRARY_PATH=/path/sass/usr/lib/x86_64-linux-gnu exec /path/sass/usr/bin/sassc "$@"\n' > bin/sassc
```

That is how the **Fluent** theme (whose sources are SCSS) and the **WhiteSur** cursors (SVGs rendered into X11 cursors) were built.

> Why not Plank, a real macOS-style dock? The same trick would work in theory, but Plank needs five or six missing libraries plus a D-Bus-activated daemon (`bamfdaemon`). Too fragile, so it was dropped.

---

## 3. The themes

| Preset | GTK + window decorations | Icons | UI font | Source |
|---|---|---|---|---|
| Windows | Fluent-round-Dark | Fluent-dark | Inter | github.com/vinceliuice (compiled with sassc) |
| macOS | WhiteSur-Dark | WhiteSur-dark + WhiteSur-cursors | Inter | github.com/vinceliuice (prebuilt release from the repository) |
| Ubuntu | Yaru-dark | Yaru-dark | Ubuntu | Debian packages `yaru-theme-*`, unpacked with `dpkg-deb -x` |

Terminal fonts: **Cascadia Mono** (Microsoft), **Meslo** (the open-source counterpart of Menlo, the macOS Terminal font), and **Ubuntu Mono**.

---

## 4. dconf: MATE's settings database

All MATE settings live in **dconf**, a key–value database organised like a file system:

```
/org/mate/desktop/interface/gtk-theme          = 'WhiteSur-Dark'
/org/mate/marco/general/theme                  = 'WhiteSur-Dark'                # window decorations
/org/mate/marco/general/button-layout          = 'close,minimize,maximize:'     # buttons on the left, macOS style
/org/mate/desktop/background/picture-filename  = '/…/Sonoma-dark-macos.png'
/org/mate/terminal/profiles/default/palette    = '#000000:#C23621:…'
```

Two commands do most of the work:

```bash
dconf dump /org/mate/ > backup.dconf   # export the whole MATE config as text (.ini format)
dconf load /org/mate/ < preset.dconf   # import it back
```

**A preset is therefore just a text file of settings**, and backing up the original look is a single `dconf dump` taken before anything is changed.

(`gsettings set …` changes the same keys one at a time, which is handy for live experiments.)

### Panels live in dconf too
The MATE panel describes each panel (“toplevel”) and each item on it (“object”):

```ini
[panel/general]
toplevel-id-list=['top', 'dock']                              # the panels
object-id-list=['menu-bar', 'clock', 'launch-firefox', …]     # the items

[panel/toplevels/dock]          # a panel
orientation='bottom'
size=60
expand=false                    # not full width…
x-centered=true                 # …but centred: that makes it a dock
auto-hide=true                  # hides itself

[panel/objects/launch-firefox]  # an item
object-type='launcher'
launcher-location='/home/…/.theme-backup/launchers/firefox-themed.desktop'
toplevel-id='dock'              # which panel it sits on
position=0                      # where on that panel
```

Item types used here:
- `applet`: Brisk Menu, window list, clock, notification area;
- `launcher`: an icon that starts an app from a `.desktop` file;
- `menu-bar`: the classic *Applications / Places / System* menu;
- `separator`: the thin vertical line in the dock.

---

## 5. The preset generator

Rather than setting up three desktops by hand, one Python script describes all three looks: `~/.theme-backup/build_presets.py`.

For each preset it:
1. reads **the user's own** original config (`original/mate.dconf`), so unrelated settings (keyboard, file manager…) are preserved;
2. removes the existing panels;
3. adds the preset's panels (`panels()`);
4. sets the theme, icons, fonts, window buttons and wallpaper (`LOOKS`);
5. sets up the terminal (`TERMINALS`);
6. writes the following into `~/.theme-backup/<preset>/`:
   - `mate.dconf`: the full MATE configuration;
   - `brisk.dconf`: Brisk Menu settings, which live under `/com/solus-project/` rather than `/org/mate/`;
   - `gnome.dconf`: dark mode for non-MATE apps (see §8);
   - `gtk.css`: visual tweaks (see §6);
   - `apply.sh`: the script that applies all of the above.

`apply.sh` then does:

```bash
dconf reset -f /org/mate/ && dconf load /org/mate/ < mate.dconf   # replace the whole MATE config
dconf load /com/solus-project/ < brisk.dconf
dconf load /org/gnome/desktop/interface/ < gnome.dconf
cp gtk.css ~/.config/gtk-3.0/gtk.css
mate-panel --replace &          # restart the panel so it re-reads everything
sleep 3; dconf load /org/mate/ < mate.dconf; mate-panel --replace &   # second pass (see §9, pitfall 2)
```

Finally, `preset` picks the right `apply.sh`, and `theme-picker` is the `zenity` window that calls `preset`.

---

## 6. CSS: the finishing touches

GTK3 is styled with **CSS**, much like a web page, and `~/.config/gtk-3.0/gtk.css` is loaded **on top of** the active theme. That makes targeted tweaks possible.

To find the right selectors, read the CSS of a theme that supports MATE (here `/usr/share/themes/BlackMATE/gtk-3.0/mate-applications.css`). It shows that each panel is a `PanelToplevel` widget with classes for its position (`.horizontal.bottom`, `.vertical.left`…).

### The macOS dock
In the macOS preset the dock is the only bottom panel, so `PanelToplevel.horizontal.bottom` targets it alone:

```css
PanelToplevel.horizontal.bottom > grid {
  background-color: rgba(38, 38, 42, 0.55);   /* translucent dark */
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 18px;                         /* rounded corners */
}
PanelToplevel.horizontal.bottom button:hover {
  background-color: rgba(255, 255, 255, 0.14); /* hover highlight */
}
```

For the rounded corners to show, **the panel itself must be transparent**. That is a dconf setting (`background type='color'`, `color='rgba(0,0,0,0)'`), and it only works with a compositor running, which Marco provides. The top menu bar uses the same technique at 45 % opacity.

### Other tweaks
```css
/* Windows: taskbar buttons tall enough to fit on a single row */
#tasklist-button { min-height: 30px; }

/* Ubuntu: open windows shown as icons only in the dock (labels made invisible) */
#tasklist-button label { font-size: 1px; color: transparent; }

/* Brisk Menu button: full-colour logo instead of the monochrome version */
.brisk-button image { -gtk-icon-style: regular; }
```

`#tasklist-button` is the widget **name** that `libwnck` gives to window-list buttons.

---

## 7. Terminals

Each preset configures the default `mate-terminal` profile (`/org/mate/terminal/profiles/default/`):

| Preset | Background | Palette | Font |
|---|---|---|---|
| Windows | `#0C0C0C` | Campbell (Windows Terminal) | Cascadia Mono 11 |
| macOS | `#1E1E1E`, 10 % transparent | Terminal.app | MesloLGS NF 11 |
| Ubuntu | `#300A24` (aubergine) | Tango | Ubuntu Mono 13 |

The palette is the 16 ANSI colours (black, red, green… then their bright variants) separated by `:`. Setting `use-theme-colors=false` is essential; otherwise the terminal takes its colours from the GTK theme.

---

## 8. Dark mode everywhere

A dark GTK theme is enough for MATE apps. **Firefox, GTK4 and libadwaita apps**, however, ignore the theme and ask the system for a **light/dark preference** through the `xdg-desktop-portal`, which in turn reads a GNOME key:

```bash
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
```

To check what the portal reports (`1` means dark):
```bash
gdbus call --session --dest org.freedesktop.portal.Desktop \
  --object-path /org/freedesktop/portal/desktop \
  --method org.freedesktop.portal.Settings.Read org.freedesktop.appearance color-scheme
```

This is what each preset's `gnome.dconf` contains.

---

## 9. Pitfalls and how they were solved

Method: after every change, **take a screenshot** (`import -window root` from ImageMagick, or `xwd -id <window>` for a single window) and zoom in on the area of interest. Most of the bugs below would have gone unnoticed otherwise.

### 1. The start button was a grey square
Brisk Menu asks for the `start-here-symbolic` icon. “Symbolic” icons are monochrome: GTK **recolours** them in a single colour. In Fluent, however, the 32 px `start-here-symbolic.svg` was actually a **symlink to the full-colour Windows logo**. Recoloured to one colour, it became a solid square.

A short Python script asking GTK which file it loads, and how, revealed this:
```python
t = Gtk.IconTheme(); t.set_custom_theme('Fluent-dark')
i = t.lookup_icon('start-here-symbolic', 32, 0)
print(i.get_filename(), i.is_symbolic())
```
Fix: remove the broken symlink, and add the CSS rule `-gtk-icon-style: regular` so Brisk uses the colour version.

### 2. The panel deleted its own configuration
The first “restore, then re-apply” test showed missing items (clock, window list). During `dconf load`, **the running panel** sees its items change one by one and deletes some of them on the way. Hence the **second pass** in `apply.sh`: the config is loaded again once the new panel has started. The round trip was then validated by comparing the resulting config with the expected one using `diff`.

### 3. Firefox vanished from the dock
Launcher files were first stored in `~/.config/mate/panel2.d/default/launchers/`, MATE's own folder. But **when MATE removes a launcher, it also deletes its file from that folder**, so switching presets wiped Firefox. Launchers now live in `~/.theme-backup/launchers/`, which MATE leaves alone.

### 4. The window list collapsed in the macOS dock
In a **non-expanded** panel (`expand=false`, required for a centred dock), the window list requests the smallest possible size and shrinks to a few pixels. Solution: the window list moved to the top bar, and the dock only holds launchers.

### 5. The Trash ignored the dock background
MATE's Trash applet runs **in a separate process**, in its own window, so it does not get the background painted by the panel's CSS, and the wallpaper showed through. Fix: a plain **launcher** that opens `caja trash:///`.

### 6. The terminal background did not change
All MATE terminals share **one server process**. The one already running picked up the new font and palette live, but not the background colour. Confirmed with `mate-terminal --disable-factory`, which starts a fresh process: there, the background was correct. Hence the documented limitation: close every terminal once.

### 7. A green line at the bottom of the screen
A hidden panel keeps **at least 1 px** on screen so it can be revealed on hover, and MATE reserves that row: maximised windows stop 1 px short of the bottom, exposing the (green) wallpaper. `xprop -root _NET_WORKAREA` shows the usable height is 1 px short. Neither `auto-hide-size=0` nor removing the panel's `_NET_WM_STRUT` reservation helped. Workaround: a copy of the wallpaper whose **bottom two rows are black**.

### 8. The macOS clock kept the wrong format
A bug in the generator: the loop that creates the panel items rewrote the 24-hour format **after** the macOS-specific setting. Fix: `setdefault` instead of plain assignment, so an existing value is not overwritten.

---

## 10. Files after installation

```
~/.themes/                 Fluent-round-*, WhiteSur-Dark, Yaru, Yaru-dark
~/.icons/                  Fluent*, WhiteSur*, Yaru*, WhiteSur-cursors
~/.local/share/fonts/      Inter, Cascadia, Meslo, Ubuntu
~/.local/share/icons/hicolor/scalable/apps/menu-emoji.svg   (🪐 macOS menu icon)
~/.local/bin/              dconf, preset, theme-picker
~/.theme-backup/
├── original -> original-YYYYMMDD-…/   your backup (mate.dconf, brisk.dconf, gnome.dconf, gtk-3.0/, restore.sh)
├── build_presets.py                   the generator
├── apply.sh                           template for each preset's apply script
├── windows/ macos/ ubuntu/            generated presets
├── launchers/                         Firefox and Trash .desktop files used by the docks
├── wallpapers/                        wallpapers
└── current                            the active preset
~/Desktop/Change Theme.desktop
```

---

## 11. Going further

- **A fourth preset:** add an entry to `LOOKS`, `TERMINALS` and `CSS` and a branch in `panels()`, then add it to the list in `~/.local/bin/theme-picker`.
- **A fully themed Firefox:** the WhiteSur and Fluent repositories ship a `firefox/` folder with a `userChrome.css`.
- **A real dock with magnification:** that needs Plank, so either administrator rights or a lot of patience with `LD_LIBRARY_PATH`.
