#!/usr/bin/env python3
"""Generates the windows / ubuntu / macos presets from the user's original MATE configuration.

Base: ~/.theme-backup/original/mate.dconf (backup made by install.sh).
Each preset is a folder in ~/.theme-backup/ containing mate.dconf, brisk.dconf, gnome.dconf,
gtk.css and apply.sh (copied from ~/.theme-backup/apply.sh).
"""
import os
import re
import shutil

HOME = os.path.expanduser('~')
ROOT = os.path.join(HOME, '.theme-backup')
BASE = os.path.join(ROOT, 'original', 'mate.dconf')
WALLPAPERS = os.path.join(ROOT, 'wallpapers')
LAUNCHERS = os.path.join(ROOT, 'launchers')  # outside panel2.d: mate-panel deletes removed launchers from there
APPS = '/usr/share/applications'


def parse(path):
    sections, cur = {}, None
    for line in open(path):
        line = line.rstrip('\n')
        m = re.match(r'^\[(.*)\]$', line)
        if m:
            cur = m.group(1)
            sections[cur] = {}
        elif '=' in line and cur is not None:
            k, v = line.split('=', 1)
            sections[cur][k] = v
    return sections


def dump(sections):
    out = []
    for name, keys in sections.items():
        out.append('[%s]' % name)
        out += ['%s=%s' % kv for kv in keys.items()]
        out.append('')
    return '\n'.join(out)


def s(v):
    return "'%s'" % v


def strlist(items):
    return '[' + ', '.join(s(i) for i in items) + ']'


# ---------- Terminals ----------
TERMINALS = {
    # Windows Terminal, "Campbell" scheme
    'windows': dict(
        bg='#0C0C0C', fg='#CCCCCC', font='Cascadia Mono 11', cursor='ibeam',
        palette='#0C0C0C:#C50F1F:#13A10E:#C19C00:#0037DA:#881798:#3A96DD:#CCCCCC:'
                '#767676:#E74856:#16C60C:#F9F1A5:#3B78FF:#B4009E:#61D6D6:#F2F2F2',
        transparent=False),
    # Ubuntu terminal: aubergine background + Tango palette
    'ubuntu': dict(
        bg='#300A24', fg='#FFFFFF', font='Ubuntu Mono 13', cursor='block',
        palette='#2E3436:#CC0000:#4E9A06:#C4A000:#3465A4:#75507B:#06989A:#D3D7CF:'
                '#555753:#EF2929:#8AE234:#FCE94F:#729FCF:#AD7FA8:#34E2E2:#EEEEEC',
        transparent=False),
    # Terminal.app (macOS), slightly transparent
    'macos': dict(
        bg='#1E1E1E', fg='#F2F2F2', font='MesloLGS NF 11', cursor='block',
        palette='#000000:#C23621:#25BC24:#ADAD27:#492EE1:#D338D3:#33BBC8:#CBCCCD:'
                '#818383:#FC391F:#31E722:#EAEC23:#5833FF:#F935F8:#14F0F0:#E9EBEB',
        transparent=True),
}


def terminal(sec, t):
    p = sec.setdefault('terminal/profiles/default', {})
    p.update({
        'visible-name': s('Default'),
        'use-theme-colors': 'false',
        'background-color': s(t['bg']),
        'foreground-color': s(t['fg']),
        'bold-color-same-as-fg': 'true',
        'allow-bold': 'true',
        'palette': s(t['palette']),
        'use-system-font': 'false',
        'font': s(t['font']),
        'cursor-shape': s(t['cursor']),
        'default-show-menubar': 'false',
        'scrollbar-position': s('hidden'),
        'background-type': s('transparent' if t['transparent'] else 'solid'),
        'background-darkness': '0.9' if t['transparent'] else '1.0',
    })


# ---------- Panels ----------
def applet(iid, toplevel, pos, end=False):
    d = {'applet-iid': s(iid), 'locked': 'true', 'object-type': s('applet'),
         'position': str(pos), 'toplevel-id': s(toplevel)}
    if end:
        d['relative-to-edge'] = s('end')
    return d


def launcher(location, toplevel, pos):
    return {'launcher-location': s(location), 'locked': 'true', 'object-type': s('launcher'),
            'position': str(pos), 'toplevel-id': s(toplevel)}


BRISK = 'BriskMenuFactory::BriskMenu'
TASKS = 'WnckletFactory::WindowListApplet'
DESKTOP = 'WnckletFactory::ShowDesktopApplet'
CLOCK = 'ClockAppletFactory::ClockApplet'
TRAY = 'NotificationAreaAppletFactory::NotificationArea'


def dock_launchers(toplevel, firefox, start=0, step=10):
    files = [os.path.join(LAUNCHERS, firefox)] + [os.path.join(APPS, f) for f in
             ('caja-browser.desktop', 'mate-terminal.desktop', 'code.desktop', 'chromium.desktop')]
    names = ['firefox', 'files', 'terminal', 'code', 'chromium']
    return {('launch-' + n): launcher(f, toplevel, start + i * step)
            for i, (n, f) in enumerate(zip(names, files))}


def panels(preset):
    if preset == 'windows':
        tops = {'bottom': {'expand': 'true', 'orientation': s('bottom'), 'screen': '0', 'size': '36'}}
        objs = {
            'start-menu': applet(BRISK, 'bottom', 0),
            'window-list': applet(TASKS, 'bottom', 10),
            'show-desktop': applet(DESKTOP, 'bottom', 0, end=True),
            'clock': applet(CLOCK, 'bottom', 10, end=True),
            'notification-area': applet(TRAY, 'bottom', 30, end=True),
        }
    elif preset == 'ubuntu':
        # Top bar with a centred clock + dock on the left
        tops = {
            'top': {'expand': 'true', 'orientation': s('top'), 'screen': '0', 'size': '28'},
            'dock': {'expand': 'true', 'orientation': s('left'), 'screen': '0', 'size': '56'},
        }
        objs = {
            'start-menu': applet(BRISK, 'top', 0),
            'clock': applet(CLOCK, 'top', 890),
            'notification-area': applet(TRAY, 'top', 0, end=True),
            **dock_launchers('dock', 'firefox.desktop'),
            'window-list': applet(TASKS, 'dock', 60),
            'show-desktop': applet(DESKTOP, 'dock', 0, end=True),
        }
    else:  # macos
        # Menu bar at the top + centred dock at the bottom
        tops = {
            'top': {'expand': 'true', 'orientation': s('top'), 'screen': '0', 'size': '28'},
            'dock': {'expand': 'false', 'orientation': s('bottom'), 'screen': '0', 'size': '60',
                     'x-centered': 'true', 'y-bottom': '0',
                     # Auto-hide: maximised windows get the whole screen
                     'auto-hide': 'true', 'auto-hide-size': '1',
                     'hide-delay': '300', 'unhide-delay': '100'},
        }
        objs = {
            # The Applications menu already carries the logo: no Brisk Menu here
            'menu-bar': {'locked': 'true', 'object-type': s('menu-bar'), 'position': '0',
                         'toplevel-id': s('top')},
            'clock': applet(CLOCK, 'top', 0, end=True),
            'notification-area': applet(TRAY, 'top', 10, end=True),
            # The window list collapses in a non-expanded panel, so it goes in the top bar
            'window-list': applet(TASKS, 'top', 400),
            **dock_launchers('dock', 'firefox-themed.desktop'),
            'dock-separator': {'locked': 'true', 'object-type': s('separator'), 'position': '50',
                               'toplevel-id': s('dock')},
            # A launcher rather than the Trash applet: the applet runs out of process and ignores the dock background
            'trash': launcher(os.path.join(LAUNCHERS, 'trash.desktop'), 'dock', 60),
        }
    return tops, objs


LOOKS = {
    'windows': dict(gtk='Fluent-round-Dark', icons='Fluent-dark', wm='Fluent-round-Dark',
                    font='Inter 10', title='Inter Semi-Bold 10',
                    buttons='menu:minimize,maximize,close',
                    wallpaper='Fluent-round-dark.png'),
    'ubuntu': dict(gtk='Yaru-dark', icons='Yaru-dark', wm='Yaru-dark',
                   font='Ubuntu 11', title='Ubuntu Bold 11',
                   buttons='menu:minimize,maximize,close',
                   wallpaper='Ubuntu-gradient.png'),
    'macos': dict(gtk='WhiteSur-Dark', icons='WhiteSur-dark', wm='WhiteSur-Dark',
                  font='Inter 10', title='Inter Semi-Bold 10',
                  buttons='close,minimize,maximize:',
                  wallpaper='Sonoma-dark-macos.png'),
}

BRISK_PREFS = {
    'windows': {'dark-theme': 'true', 'label-visible': 'false'},
    'ubuntu': {'dark-theme': 'true', 'label-visible': 'false'},
    'macos': {'dark-theme': 'true', 'label-visible': 'false'},
}

CSS_COMMON = '''/* Brisk Menu button: full-colour logo instead of the symbolic version */
.brisk-button image { -gtk-icon-style: regular; }
'''
CSS = {
    'windows': CSS_COMMON + '''
/* Taskbar: a single row of buttons, tall enough */
#tasklist-button { min-height: 30px; padding: 0 8px; }
''',
    'ubuntu': CSS_COMMON + '''
/* Dock: open windows shown as icons only */
#tasklist-button { min-width: 52px; min-height: 44px; padding: 0 0 0 14px; }
#tasklist-button label { font-size: 1px; color: transparent; }
''',
    'macos': CSS_COMMON + '''
/* macOS-style dock (the only bottom panel in this preset) */
PanelToplevel.horizontal.bottom > grid {
  background-color: rgba(38, 38, 42, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 18px;
  padding: 0 6px;
  margin: 0 0 4px 0;
}
PanelToplevel.horizontal.bottom button {
  margin: 4px 3px;
  padding: 2px;
  border-radius: 12px;
  background: none;
  border: none;
  box-shadow: none;
}
PanelToplevel.horizontal.bottom button:hover {
  background-color: rgba(255, 255, 255, 0.14);
}
PanelToplevel.horizontal.bottom PanelSeparator {
  background: none;
  border: none;
  box-shadow: none;
  color: rgba(255, 255, 255, 0.3);
}

/* Translucent menu bar */
PanelToplevel.horizontal.top > grid {
  background-color: rgba(20, 20, 24, 0.45);
}
PanelToplevel.horizontal.top #tasklist-button {
  background: none;
  border: none;
  box-shadow: none;
  border-radius: 6px;
  padding: 0 8px;
}
PanelToplevel.horizontal.top #tasklist-button:checked,
PanelToplevel.horizontal.top #tasklist-button:hover {
  background-color: rgba(255, 255, 255, 0.15);
}
''',
}


def build(preset):
    sec = parse(BASE)
    for name in list(sec):
        if name.startswith(('panel/objects/', 'panel/toplevels/')):
            del sec[name]
    tops, objs = panels(preset)
    sec.setdefault('panel/general', {}).update({
        'toplevel-id-list': strlist(tops), 'object-id-list': strlist(objs)})
    for k, v in tops.items():
        sec['panel/toplevels/' + k] = v
    if preset == 'macos':
        # Transparent panels: the CSS draws the dock's rounded background
        sec['panel/toplevels/dock/background'] = {'type': s('color'), 'color': s('rgba(0,0,0,0)')}
        sec['panel/toplevels/top/background'] = {'type': s('color'), 'color': s('rgba(0,0,0,0)')}
        # macOS-style clock: “Thu 1 Oct  16:15”
        sec['panel/objects/clock/prefs'] = {'format': s('custom'), 'custom-format': s('%a %-d %b  %H:%M')}
        sec['peripherals-mouse'] = {'cursor-theme': s('WhiteSur-cursors')}
        # Top-left menu icon (instead of the Apple logo)
        sec['panel/menubar'] = {'icon-name': s('menu-emoji')}  # ~/.local/share/icons/hicolor (Twemoji 🪐)
    for k, v in objs.items():
        sec['panel/objects/' + k] = v
        if v.get('applet-iid') == s(CLOCK):
            sec.setdefault('panel/objects/%s/prefs' % k, {'format': s('24-hour'), 'custom-format': s('')})

    look = LOOKS[preset]
    sec.setdefault('desktop/interface', {}).update({
        'gtk-theme': s(look['gtk']), 'icon-theme': s(look['icons']),
        'font-name': s(look['font']), 'document-font-name': s(look['font'])})
    sec.setdefault('caja/desktop', {})['font'] = s(look['font'])
    sec.setdefault('desktop/font-rendering', {}).update({
        'antialiasing': s('rgba'), 'hinting': s('slight')})
    sec.setdefault('marco/general', {}).update({
        'theme': s(look['wm']), 'titlebar-font': s(look['title']),
        'titlebar-uses-system-font': 'false', 'button-layout': s(look['buttons'])})
    sec.setdefault('desktop/background', {}).update({
        'picture-filename': s(os.path.join(WALLPAPERS, look['wallpaper'])),
        'picture-options': s('zoom')})
    terminal(sec, TERMINALS[preset])

    d = os.path.join(ROOT, preset)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'mate.dconf'), 'w').write(dump(sec))
    brisk = '[brisk-menu]\n' + ''.join('%s=%s\n' % kv for kv in BRISK_PREFS[preset].items())
    open(os.path.join(d, 'brisk.dconf'), 'w').write(brisk)
    open(os.path.join(d, 'gtk.css'), 'w').write(CSS[preset])
    gnome = {'color-scheme': s('prefer-dark'), 'gtk-theme': s(look['gtk']),
             'icon-theme': s(look['icons'])}
    if preset == 'macos':
        gnome['cursor-theme'] = s('WhiteSur-cursors')
    open(os.path.join(d, 'gnome.dconf'), 'w').write(dump({'/': gnome}))
    shutil.copy(os.path.join(ROOT, 'apply.sh'), os.path.join(d, 'apply.sh'))
    os.chmod(os.path.join(d, 'apply.sh'), 0o755)
    print('preset', preset, '->', d)


if __name__ == '__main__':
    import sys
    for p in sys.argv[1:] or ['windows', 'ubuntu', 'macos']:
        build(p)
