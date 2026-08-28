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
    # Checked here and not only at startup. A served rebuild is triggered by editing a source,
    # and an edited OpenAPI description is exactly the thing the address check exists for — a
    # server URL changed while the preview is open would otherwise reach the try-it page
    # unvalidated, and that page sends a maintainer's real bearer token wherever it points.
    #
    # Raising rather than exiting: MkDocs catches this, keeps serving what it already built, and
    # prints the reason. Killing the server on a typo would be worse than showing stale content.
    if _module.check():
        raise RuntimeError("the site's inputs are not in a state that can be served — see above")
    _module.stage()
