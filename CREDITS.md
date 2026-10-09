# Credits and Licences

This project bundles the following open-source works. Many thanks to their authors.

| Component | Author / source | Licence |
|---|---|---|
| Fluent GTK theme, Fluent icon theme | vinceliuice: [Fluent-gtk-theme](https://github.com/vinceliuice/Fluent-gtk-theme), [Fluent-icon-theme](https://github.com/vinceliuice/Fluent-icon-theme) | GPL-3.0 |
| WhiteSur GTK theme | vinceliuice: [WhiteSur-gtk-theme](https://github.com/vinceliuice/WhiteSur-gtk-theme) | MIT |
| WhiteSur icon theme, WhiteSur cursors | vinceliuice: [WhiteSur-icon-theme](https://github.com/vinceliuice/WhiteSur-icon-theme), [WhiteSur-cursors](https://github.com/vinceliuice/WhiteSur-cursors) | GPL-3.0 |
| Fluent wallpapers | vinceliuice: [Fluent-kde](https://github.com/vinceliuice/Fluent-kde) | GPL-3.0 |
| WhiteSur / Sonoma wallpapers | vinceliuice: [WhiteSur-wallpapers](https://github.com/vinceliuice/WhiteSur-wallpapers) | MIT |
| Yaru theme and icons | Canonical and the Ubuntu community: [Yaru](https://github.com/ubuntu/yaru) (Debian packages `yaru-theme-gtk`, `yaru-theme-icon`) | GPL-3.0, CC BY-SA 4.0 |
| Inter font | Rasmus Andersson: [rsms.me/inter](https://rsms.me/inter/) | SIL OFL 1.1 |
| Cascadia Code / Mono fonts | Microsoft: [cascadia-code](https://github.com/microsoft/cascadia-code) | SIL OFL 1.1 |
| Meslo LG font (MesloLGS NF) | André Berg; Nerd Font patch from [romkatv/powerlevel10k-media](https://github.com/romkatv/powerlevel10k-media) | Apache 2.0 |
| Ubuntu / Ubuntu Mono fonts | Canonical (Debian package `fonts-ubuntu`) | Ubuntu Font Licence 1.0 |
| 🪐 emoji (macOS menu icon) | [Twemoji](https://github.com/jdecked/twemoji) | CC BY 4.0 (graphics) |
| `dconf` binary | GNOME (Debian package `dconf-cli`) | LGPL-2.1+ |
| “Ubuntu-gradient” wallpaper | generated with ImageMagick for this project | — |

## Modifications

- **Fluent icon theme:** removed the `32/status/start-here-symbolic.svg` symlinks. They pointed to a full-colour icon, which GTK rendered as a solid square when recolouring it as a symbolic icon.
- **Sonoma wallpaper:** cropped to 1920×1080, with the bottom two rows darkened so the 1 px strip left by MATE's auto-hiding dock is invisible.

## This project

The scripts (`install.sh`, `uninstall.sh`, `build_presets.py`, `apply.sh`, `restore.sh`, `preset`, `theme-picker`) and the documentation are released under the MIT licence; see [LICENSE](LICENSE).
