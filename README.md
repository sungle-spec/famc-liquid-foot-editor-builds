# LF+ Editor — packaging & OS builds

This repo produces the **standalone Windows / Linux / macOS bundles** of the
[LF+ Editor](https://github.com/sungle-spec/famc-liquid-foot-usb-editor) and hosts their
**Releases**. The application source (and the web version, docs, tests) lives in the source
repo; this one holds only what packaging needs:

```
packaging/lfeditor.spec        PyInstaller spec (one-dir bundle; .app wrap on macOS)
packaging/entry.py             frozen-app entry point
packaging/make_icons.py        generates app.png / app.ico / app.icns
packaging/icons/               the generated icons
packaging/linux/               AppRun + .desktop + make_appimage.sh (AppImage)
.github/workflows/build.yml    3-OS build + selftest + release workflow
```

## Releases

Grab the bundle for your OS from this repo's
[Releases](https://github.com/sungle-spec/famc-liquid-foot-editor-builds/releases):

| OS | Asset | First-launch note |
|----|-------|-------------------|
| Windows | `LFPlusEditor-<v>-windows-x64.zip` → run `LFPlusEditor.exe` | unsigned: SmartScreen → *More info → Run anyway*; needs the FTDI VCP driver for USB-serial |
| Linux | `LFPlusEditor-<v>-x86_64.AppImage` → `chmod +x` and run | serial: `sudo usermod -aG dialout $USER` |
| macOS | `LFPlusEditor-<v>-macos-arm64.zip` → `LF+ Editor (native).app` | unsigned: right-click → **Open → Open** |

Verify a download with the release's `SHA256SUMS.txt` (`sha256sum -c`, macOS `shasum -a 256 -c`).

## Building

**CI (the normal path):** Actions → *build* → *Run workflow*. Inputs:

- `ref` — the source branch / tag / SHA to build (default `main`)
- `release_tag` — optional; when set (e.g. `v0.0.3`, must equal the source's
  `lfeditor.__version__`), the three bundles + `SHA256SUMS.txt` are published as a Release here.
  Left empty, the bundles land as run artifacts only.

Each OS runner checks out the source, overlays `packaging/`, builds with PyInstaller, and runs
the frozen binary's `--selftest` before packaging — a broken bundle fails the job, not the user.

> The source repo is public — the workflow checks it out anonymously, no secrets needed.

**Locally** (on the OS you're targeting — PyInstaller can't cross-compile):

```bash
git clone https://github.com/sungle-spec/famc-liquid-foot-usb-editor src
cp -R packaging src/packaging
cd src
pip install -r requirements-dev.txt pillow pyinstaller
python packaging/make_icons.py
pyinstaller --noconfirm packaging/lfeditor.spec
./dist/LFPlusEditor/LFPlusEditor --selftest
```

Code signing (macOS notarization / Windows Authenticode) is not wired up — it needs signing
certificates; the unsigned-launch steps above are the documented workaround.
