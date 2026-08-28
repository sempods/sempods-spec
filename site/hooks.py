"""Re-stage the sources before MkDocs reads them.

Only matters while serving. MkDocs watches the directory it renders, and `site/build.py`
renders a copy — so without this, the rebuild triggered by editing a chapter would read the
copy made when the server started and render the old text. A build run once from the command
line stages immediately beforehand and would not need this; it is harmless there.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_build = Path(__file__).resolve().parent / "build.py"
_spec = importlib.util.spec_from_file_location("sempods_site_build", _build)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)


def on_pre_build(config, **kwargs):  # noqa: ARG001 - MkDocs passes more than this needs
    _module.stage()
