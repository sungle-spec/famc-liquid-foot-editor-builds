# PyInstaller spec for the FAMC Liquid Foot+ Editor (PySide6 desktop app).
#
# Build a standalone, no-terminal app so musicians never touch a venv:
#   pip install pyinstaller
#   python packaging/make_icons.py               # optional: app icon (needs Pillow for .ico)
#   pyinstaller packaging/lfeditor.spec          # run from the repo root
# Output: a one-dir bundle in dist/LFPlusEditor (wrapped into "LF+ Editor (native).app" on macOS).
# CI zips it per-OS; the Linux build is then turned into an AppImage (see packaging/linux/).
#
# No reference data is bundled — the app starts empty until the user opens a .syx (or File →
# Load Factory Defaults). The third-party firmware/dumps in reference/ are never shipped.
#
# REMAINING MANUAL STEPS (need the target OS + a signing identity):
#   - macOS: codesign + notarize the .app (else Gatekeeper blocks it).
#   - Windows: optionally Authenticode-sign the .exe (else SmartScreen warns).
#   - Test serial/MIDI port discovery on each OS with a real device.

import os
import re
import sys

block_cipher = None
ROOT = os.path.abspath(os.getcwd())

# --- single-source the version from lfeditor/__init__.py (no import side effects) -------------
def _read_version() -> str:
    init = os.path.join(ROOT, "lfeditor", "__init__.py")
    with open(init, encoding="utf-8") as fh:
        m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', fh.read())
    return m.group(1) if m else "0.0.0"

VERSION = _read_version()

# --- per-OS icon: embed whichever the icon generator produced; None if it wasn't run ----------
def _icon() -> str | None:
    icons = os.path.join(ROOT, "packaging", "icons")
    name = {"win32": "app.ico", "darwin": "app.icns"}.get(sys.platform, "app.png")
    path = os.path.join(icons, name)
    return path if os.path.exists(path) else None

ICON = _icon()

hiddenimports = [
    "serial.tools.list_ports",   # USB-serial port discovery
    "rtmidi",                    # mido backend for MIDI ports
    "mido.backends.rtmidi",
]

a = Analysis(
    [os.path.join(ROOT, "packaging", "entry.py")],
    pathex=[ROOT],
    binaries=[],
    datas=[
        # ship the bundled factory-default backups (File → Load Factory Defaults)
        (os.path.join(ROOT, "lfeditor", "resources", "factory"),
         os.path.join("lfeditor", "resources", "factory")),
        # ship LICENSE two levels up from lfeditor/ui so the About dialog reads the real text
        (os.path.join(ROOT, "LICENSE"), "."),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# A space-free binary/dir name keeps Linux AppImage tooling and shell scripts happy; the
# user-facing macOS bundle below is still named "LF+ Editor (native).app".
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="LFPlusEditor",
    console=False,
    disable_windowed_traceback=False,
    icon=ICON,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name="LFPlusEditor")

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="LF+ Editor (native).app",
        icon=ICON,
        bundle_identifier="com.sungle.lfplus-editor-native",
        info_plist={
            "NSHighResolutionCapable": True,
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
        },
    )
