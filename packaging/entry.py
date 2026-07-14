"""PyInstaller entry point.

Uses an *absolute* import so the frozen app has a real package context. (Pointing PyInstaller
directly at ``lfeditor/__main__.py`` runs it as top-level ``__main__`` with no parent package, so
its ``from .ui.app`` relative import fails at launch — this launcher avoids that.) The
``python -m lfeditor`` path still goes through ``lfeditor/__main__.py``.
"""
from lfeditor.ui.app import main

if __name__ == "__main__":
    main()
