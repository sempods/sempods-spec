#!/usr/bin/env python3
"""Assemble and render https://spec.sempods.org.

MkDocs refuses a `docs_dir` that contains its own configuration, and pointing it at the
repository root would publish the agent instructions along with the specification. So the
site is staged into a directory this script owns and `.gitignore` hides: the normative tree
is copied, never edited, and nothing under `spec/` has to know a website exists.

Run `python3 site/build.py` from anywhere; `--serve` rebuilds and watches instead.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
STAGE = SITE / "_stage"

# The public pod the try-it button talks to. THIS IS THE ONLY PLACE IT IS WRITTEN.
#
# It is deliberately not in the OpenAPI descriptions: those are normative, and a
# specification that names one operator's deployment has confused the contract with an
# instance of it. Their `servers` block stays on `example.org`/`alice`, and the staged copy
# rendered for the try-it page gets these values substituted in.
#
# Switching to a different demo pod is an edit to these two strings.
DEMO_ORIGIN = "https://sempods.org"
DEMO_POD = "aaltra"

# Chapters, in reading order. The nav in `mkdocs.yml` repeats this order; a chapter added
# here and forgotten there is caught by `--check`.
CORE = ["index", "contexts", "grants", "auth", "lod-crud", "sparql", "find"]
MODULES = ["oidc", "media", "mcp"]


def stage() -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    docs = STAGE / "docs"
    docs.mkdir(parents=True)

    shutil.copytree(ROOT / "spec", docs / "spec")
    shutil.copy(ROOT / "GOVERNANCE.md", docs / "GOVERNANCE.md")
    shutil.copytree(ROOT / "vocabulary", docs / "vocabulary")
    shutil.copy(SITE / "index.md", docs / "index.md")

    api = docs / "api"
    api.mkdir()
    shutil.copy(SITE / "api" / "index.html", api / "index.html")
    for src in sorted((ROOT / "openapi").glob("*.yaml")):
        (api / src.name).write_text(with_demo_pod(src.read_text()))

    shutil.copy(SITE / "mkdocs.yml", STAGE / "mkdocs.yml")
    (STAGE / "docs" / "CNAME").write_text("spec.sempods.org\n")


# Each substitution is checked on its own. Applying them as one pass and asking whether the
# text changed is the shape that looks right and is not: either one matching hides the other
# having stopped matching, and the half that silently survives is a try-it button aimed at
# `example.org`.
SUBSTITUTIONS = (
    ("default: 'https://example.org'", f"default: '{DEMO_ORIGIN}'"),
    ("default: alice", f"default: {DEMO_POD}"),
)


def with_demo_pod(yaml: str) -> str:
    """Point a staged description's server variables at the demo pod.

    Substring replacement rather than a YAML round-trip, on purpose: parsing and re-emitting
    would reformat a hand-written file whose layout and comments are part of how it reads,
    and both defaults are written one way across all four descriptions.
    """
    for old, new in SUBSTITUTIONS:
        yaml = yaml.replace(old, new)
    return yaml


def check() -> int:
    """Everything this build assumes, asserted before it can ship a broken page."""
    problems = []

    for name in CORE:
        if not (ROOT / "spec" / "core" / f"{name}.md").is_file():
            problems.append(f"spec/core/{name}.md is listed in CORE but does not exist")
    for name in MODULES:
        if not (ROOT / "spec" / "modules" / f"{name}.md").is_file():
            problems.append(f"spec/modules/{name}.md is listed in MODULES but does not exist")

    # The reverse direction, which is the one that goes wrong quietly: a chapter written and
    # never added here renders nowhere and nobody notices, because the build still succeeds.
    for path in sorted((ROOT / "spec" / "core").glob("*.md")):
        if path.stem not in CORE and path.stem != "README":
            problems.append(f"{path.relative_to(ROOT)} exists but is in no nav list")
    for path in sorted((ROOT / "spec" / "modules").glob("*.md")):
        if path.stem not in MODULES and path.stem != "README":
            problems.append(f"{path.relative_to(ROOT)} exists but is in no nav list")

    descriptions = sorted((ROOT / "openapi").glob("*.yaml"))
    if not descriptions:
        problems.append("openapi/ holds no description; the try-it page would render nothing")
    for src in descriptions:
        text = src.read_text()
        if "servers:" not in text:
            problems.append(f"{src.relative_to(ROOT)} has no servers block to point at a pod")
        else:
            for old, _ in SUBSTITUTIONS:
                if old not in text:
                    problems.append(
                        f"{src.relative_to(ROOT)} no longer contains {old!r}, so the staged "
                        f"copy would keep the specification's placeholder and aim the "
                        f"try-it button at a host nobody operates")

    nav = (SITE / "mkdocs.yml").read_text()
    for name in CORE:
        if f"spec/core/{name}.md" not in nav:
            problems.append(f"spec/core/{name}.md is in CORE but missing from the mkdocs nav")
    for name in MODULES:
        if f"spec/modules/{name}.md" not in nav:
            problems.append(f"spec/modules/{name}.md is in MODULES but missing from the nav")

    for problem in problems:
        print(f"error: {problem}", file=sys.stderr)
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="rebuild and watch on :8000")
    parser.add_argument("--check", action="store_true", help="verify inputs, render nothing")
    args = parser.parse_args()

    failed = check()
    if failed or args.check:
        return failed

    stage()
    command = ["mkdocs", "serve" if args.serve else "build"]
    if not args.serve:
        command += ["--strict"]
    return subprocess.call(command, cwd=STAGE)


if __name__ == "__main__":
    raise SystemExit(main())
