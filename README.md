# MATE Theme Presets: Windows · macOS · Ubuntu

Three complete desktop looks for the **MATE** desktop, installed **without root access**.

Everything goes into your home directory: themes, icons, cursors, fonts, panel layouts, terminal colours and wallpapers. Your current setup is backed up first, so you can switch back at any time. It was built for locked-down lab machines (Debian 13 + MATE) where users have no `sudo`, but it works on any MATE desktop.

| Preset | GTK theme / icons | Layout | Terminal |
|---|---|---|---|
| **Windows** | Fluent (dark) | Single taskbar at the bottom with a start menu | Windows Terminal “Campbell” palette, Cascadia Mono |
| **macOS** | WhiteSur (dark) + macOS cursors | Translucent menu bar at the top, rounded auto-hiding dock at the bottom | Terminal.app palette, Meslo, slightly transparent |
| **Ubuntu** | Yaru (dark) | Top bar with a centred clock, launcher dock on the left | Ubuntu aubergine background, Ubuntu Mono |
| **Default** | your previous theme | your previous layout | your previous terminal |

Every preset also turns on the system-wide **dark mode**, so Firefox and GTK4/libadwaita apps follow it too.

---

## Requirements

- A **MATE** session on X11 with a compositor (Marco's built-in compositor is enough)
- `python3`, `zenity`, and `libdconf1` (present on any MATE install)
- About **350 MB** of free space in your home directory
- Optional: **Brisk Menu** (`mate-applet-brisk-menu`) for the Windows/Ubuntu start menu

No root access and no package installation are needed.

---

## Installation

1. **Get the project**:
   ```bash
   git clone https://github.com/Siin0pe/mate-theme-presets.git
   cd mate-theme-presets
   ```
   or download `theme-presets.zip` from the [latest release](https://github.com/Siin0pe/mate-theme-presets/releases/latest), then:
   ```bash
   unzip theme-presets.zip
   cd theme-presets
   ```

2. **Run the installer**:
   ```bash
   ./install.sh
   ```
   The installer:
   - backs up your current desktop settings to `~/.theme-backup/original/` (once; an existing backup is never overwritten);
   - copies themes, icons, cursors and fonts into your home directory;
   - generates the three presets **from your own configuration**, so your other settings are kept;
   - adds a **“Change Theme”** launcher to your desktop;
   - asks which preset to apply.

   To apply a preset straight away, pass it as an argument: `./install.sh macos`

> The screen flickers for 2–3 seconds whenever a preset is applied while the MATE panel restarts. This is expected.

---

## Usage

**From the desktop:** double-click **Change Theme**, pick a preset, and confirm.

**From a terminal:**
```bash
preset windows     # Windows 11 look
preset macos       # macOS look
preset ubuntu      # Ubuntu look
preset original    # your original theme
```
If `preset` is not found, open a new terminal or run `~/.local/bin/preset`.

### Tips
- **Windows / Ubuntu:** the **Super** key opens the start menu.
- **macOS:** the dock hides itself. Move the pointer to the very bottom of the screen to reveal it. The application menu is the 🪐 icon in the top-left corner.

---

## Reverting and uninstalling

- **Back to your original theme:** `preset original`, or choose **Default** in the Change Theme window.
- **Remove everything:**
  ```bash
  cd mate-theme-presets      # or theme-presets if you used the zip
  ./uninstall.sh
  ```
  This restores your original theme and removes the installed themes, icons, fonts, commands and desktop launcher. The backup in `~/.theme-backup` is kept on purpose; delete it manually if you no longer need it.

---

## Customising

All three presets are defined in a single file: **`~/.theme-backup/build_presets.py`**.

| What | Where |
|---|---|
| Terminal colours and fonts | `TERMINALS` |
| GTK theme, icons, fonts, window buttons, wallpaper | `LOOKS` |
| Panels, docks and their contents | `panels()` |
| Visual tweaks (rounded dock, transparency…) | `CSS` |

After editing:
```bash
python3 ~/.theme-backup/build_presets.py   # regenerate the presets
preset macos                               # re-apply
```

- **macOS menu icon:** replace `~/.local/share/icons/hicolor/scalable/apps/menu-emoji.svg` with any SVG (for example from [Twemoji](https://github.com/jdecked/twemoji/tree/main/assets/svg)), then run `preset macos`.
- **Wallpapers:** replace an image in `~/.theme-backup/wallpapers/` with one of the same name, or change the file name in `LOOKS`.

---

## Known limitations

- **Open terminals:** fonts and colours update immediately, but the **background colour** only changes once every terminal window has been closed, or after logging in again. All MATE terminals share one server process, which does not reload that setting.
- **Firefox** follows dark mode automatically. If it stays light, set *Settings → General → Website appearance* to *Automatic*.
- **macOS dock:** there is no magnification effect and no running-app indicators; the MATE panel cannot do this without Plank.
- **macOS dock:** MATE keeps a 1 px strip of a hidden panel on screen, and windows cannot cover it. The bundled wallpaper has a black bottom edge so the strip is invisible.
- **Dock launchers** point to Firefox (`/opt/firefox`), Caja, MATE Terminal, VS Code and Chromium, the apps on the machines this was built for. Edit `dock_launchers()` in `build_presets.py` to change them.

---

## Documentation

- [**HOW_IT_WORKS.md**](HOW_IT_WORKS.md): a detailed walkthrough of how the presets are built, including every pitfall met along the way and how it was solved.
- [**CREDITS.md**](CREDITS.md): the upstream projects bundled here and their licences.

## Licence

The scripts and documentation are released under the [MIT licence](LICENSE). Bundled themes, icons, cursors, fonts and wallpapers keep their original licences, listed in [CREDITS.md](CREDITS.md).
