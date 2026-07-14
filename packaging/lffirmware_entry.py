"""PyInstaller entry point for the LF+ Firmware Loader.

Absolute imports so the frozen app has a real package context (same rationale as entry.py).
Arguments -> CLI, no arguments -> GUI, mirroring `python -m lffirmware`.
"""
import sys

if len(sys.argv) > 1:
    from lffirmware.cli import main
else:
    from lffirmware.gui import main

sys.exit(main())
