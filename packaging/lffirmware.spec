# PyInstaller spec for the LF+ Firmware Loader (beta) — the standalone flasher/recovery tool.
# Built alongside the editor from the same source checkout:
#   pyinstaller packaging/lffirmware.spec        # run from the source-repo root
# Output: dist/LFFirmwareLoader (one-dir; wrapped into "LF+ Firmware Loader.app" on macOS).
#
# Ships NO firmware images (FAMC's binaries stay unredistributed) — only the SHA-256
# allowlist inside lffirmware/known_images.py. See docs/FIRMWARE_LOADER.md.

import os
import re
import sys

block_cipher = None
ROOT = os.path.abspath(os.getcwd())


def _read_version() -> str:
    init = os.path.join(ROOT, "lffirmware", "__init__.py")
    with open(init, encoding="utf-8") as fh:
        m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', fh.read())
    return m.group(1) if m else "0.0.0"


VERSION = _read_version()


def _icon() -> str | None:
    icons = os.path.join(ROOT, "packaging", "icons")
    name = {"win32": "app.ico", "darwin": "app.icns"}.get(sys.platform, "app.png")
    path = os.path.join(icons, name)
    return path if os.path.exists(path) else None


ICON = _icon()

hiddenimports = [
    "rtmidi",
    "mido.backends.rtmidi",
    "lfeditor.ui.theme",   # cosmetic: the loader reuses the editor stylesheet when present
]

a = Analysis(
    [os.path.join(ROOT, "packaging", "lffirmware_entry.py")],
    pathex=[ROOT],
    binaries=[],
    datas=[(os.path.join(ROOT, "LICENSE"), ".")],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="LFFirmwareLoader",
    console=False,
    disable_windowed_traceback=False,
    icon=ICON,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name="LFFirmwareLoader")

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="LF+ Firmware Loader.app",
        icon=ICON,
        bundle_identifier="com.sungle.lfplus-firmware-loader",
        info_plist={
            "NSHighResolutionCapable": True,
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
        },
    )
