# Repository checks

This informative guide describes the checks in this repository's revision: the
[requirement checker](../../.github/scripts/check-requirements.py),
[example runner](../../.github/scripts/check-examples.py),
[Context representation checker](../../.github/scripts/check-context-registry.py) and
[site builder](../../site/build.py).
Read it at the same Git revision as those sources.

## What a passing run establishes

| Check | Evidence and limits |
|---|---|
| Offline links and fragments | Local links and requirement anchors resolve. It excludes `site/`, whose hand-written links address the staged layout; the full site render checks those. It does not verify remote destinations. |
| Requirement identifiers | Chapter/area placement, identifier changes against the base, OpenAPI requirement citations and the generated index are consistent. It enforces the observable part of [governance's identifier window](../../GOVERNANCE.md#deleting-and-renumbering-before-01); read notices as well as failures. It cannot detect an external adopter or prove semantic equivalence. |
| ACP runner self-test | Deliberately failing and boundary cases check that the runner still detects errors. Run it before the scenarios. |
| Worked scenarios | The supplied fixture expectations agree with the runner's ACP evaluations and model composition. A green run checks those cases; it neither prescribes ACP nor demonstrates a running implementation. [Examples](../../examples/README.md) owns the fixture format and assumptions. |
| Context registry representations | Actual OpenAPI examples and guide JSON-LD validate against their schemas and preserve registry RDF through N-Quads round trips; malformed legacy shapes are rejected. No HTTP, authorization, caching or lifecycle implementation is tested. |
| Site navigation regression tests | Source-relative links survive relocation and select the build commit; dirty previews and snapshot metadata are distinguished. |
| Full site build | Inputs, the demo-pod destination and staged links survive strict rendering. The destination check prevents the try-it page from sending requests, including authenticated ones, to another host. It does not exercise the live OAuth or request flow. |

These are repository checks and example execution, not product conformance claims. They do not
establish that a pod satisfies the specification. Implementation-specific conformance reports
belong with their implementation; ownership of a future implementation-neutral suite is a
separate decision. Normative adoption and publication follow [governance](../../GOVERNANCE.md).

## Set up the tools

Run from the repository root. Tools are not vendored. Read `python3 -V` before creating the
virtualenv: the site lock was resolved on Python 3.14, which CI uses. Hash checking verifies
artifacts, not the interpreter that resolves them.

```bash
brew install lychee
python3 -m venv site/.venv
site/.venv/bin/pip install --require-hashes -r site/requirements.txt
export PATH="$PWD/site/.venv/bin:$PATH"
```

The example runner also needs the parser dependencies pinned in
[Examples §Dependency](../../examples/README.md#dependency). Install them into the same environment.
The site builder looks up `mkdocs` on `PATH`; the scripts use `python3`.

The Context representation checker also needs the validator stack pinned in the Examples workflow:

```bash
python3 -m pip install rdflib==7.6.0 pyparsing==3.3.2 PyYAML==6.0.3 jsonschema==4.25.1 attrs==26.1.0 jsonschema-specifications==2025.9.1 referencing==0.37.0 rpds-py==2026.6.3
```

## Before requesting review

```bash
lychee --offline --include-fragments --no-progress --exclude-path site .
.github/scripts/check-requirements.py origin/main
.github/scripts/check-examples.py --self-test
.github/scripts/check-examples.py
python3 .github/scripts/check-context-registry.py
python3 -m unittest discover -s site -p 'test_*.py'
python3 site/build.py
```

Pass the base ref: without it the requirement disappearance comparison does not run. Use the PR's
actual base if it differs from `origin/main`. Adding or withdrawing requirements also regenerates
the committed index:

```bash
.github/scripts/check-requirements.py --write-index
```

The full render is required: `python3 site/build.py --check` checks inputs and returns before
staging, so it cannot validate staged links. `python3 site/build.py --serve` renders and watches
on port 8000 for local editing.

Report the commands, results and skipped checks in the work record. A substitute link checker
written for an individual change cannot establish the required fragment validation; install the
tool or report that check as not run. Review prose and semantic effects alongside the checks:
unchanged IDs, valid links and passing fixtures cannot establish an unchanged contract.

The site build needs a Git checkout to identify its source commit. Local uncommitted changes produce
an explicitly marked preview; source links identify its base commit. Pages uses `--require-clean`
before publishing, and every rendered page links its revision and original artifacts. The API page's
demo-address copies are separate from those original sources.
