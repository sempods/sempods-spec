# Repository checks

This informative guide describes the checks in this repository's revision: the
[requirement checker](../../.github/scripts/check-requirements.py),
[example runner](../../.github/scripts/check-examples.py),
[Context representation checker](../../.github/scripts/check-context-registry.py) and
[site builder](../../site/build.py).
The [MCP experiment](#mcp-endpoint-discovery-experiment) separately records bounded client behavior
and known validation failures.
Read it at the same Git revision as those sources.

## What a passing run establishes

| Check | Evidence and limits |
|---|---|
| Offline links and fragments | Local links and requirement anchors resolve. It excludes `site/`, whose hand-written links address the staged layout; the full site render checks those. It does not verify remote destinations. |
| Requirement identifiers | Chapter/area placement, identifier changes against the base, OpenAPI requirement citations and the generated index are consistent. It enforces the observable part of [governance's identifier window](../../GOVERNANCE.md#deleting-and-renumbering-before-01); read notices as well as failures. It cannot detect an external adopter or prove semantic equivalence. |
| ACP runner self-test | Deliberately failing and boundary cases check that the runner still detects errors. Run it before the scenarios. |
| Worked scenarios | The supplied fixture expectations agree with the runner's ACP evaluations and model composition. A green run checks those cases; it neither prescribes ACP nor demonstrates a running implementation. [Examples](../../examples/README.md) owns the fixture format and assumptions. |
| Context registry representations | Actual OpenAPI examples and guide JSON-LD validate against their schemas and preserve registry RDF through N-Quads round trips; malformed legacy shapes are rejected. Unicode IRIs and language-tagged text are accepted; invalid IRIs are rejected. The Context module's references resolve without core, and shared components agree. Registry reads and creation document their authentication challenges; their successful and error responses reference the same cache guarantee. Creation dates admit XSD forms beyond RFC 3339; the checker does not validate the full XSD lexical space. No HTTP, authorization, caching or lifecycle implementation is tested. |
| Site navigation regression tests | Source-relative links survive relocation and select the build commit; dirty previews and snapshot metadata are distinguished. |
| Full site build | Inputs, the demo-pod destination and staged links survive strict rendering. The destination check prevents the try-it page from sending requests, including authenticated ones, to another host. It does not exercise the live OAuth or request flow. |

These are repository checks and example execution, not product conformance claims. They do not
establish that a pod satisfies the specification. Implementation-specific conformance reports
belong with their implementation; ownership of a future implementation-neutral suite is a
separate decision. Normative adoption and publication follow [governance](../../GOVERNANCE.md).

## MCP endpoint discovery experiment

[`probe-mcp-endpoint.mjs`](../../.github/scripts/probe-mcp-endpoint.mjs) exercises the
[MCP discovery and resource contract](../../spec/modules/mcp.md#discovery-and-resource-binding)
with the **unmodified official TypeScript SDK 1.30.1**, Node **22.19.0** and MCP **2025-11-25**.
It is a bounded interoperability experiment, separate from the required repository checks and
from a conformance suite. It installs no sempods-specific discovery, resource-validation or fetch
hook. Provider callbacks only store client information, tokens and the PKCE verifier, and receive
the authorization redirect. The SDK is configured with only the MCP endpoint.

The fixture listens on an ephemeral IPv4 loopback port with TLS certificate verification enabled.
It supplies synthetic resource/issuer metadata, registration, PKCE code exchange, signed tokens,
refresh and two MCP tools. The harness follows the authorization URL and reads the redirect;
consent is a fixture decision, not an exercised browser screen. After code exchange it explicitly
retries the challenged tool call through the SDK. It does not establish automatic desktop-client
retry behavior, real grants, browser consent, production TLS deployment or Kotlin conformance.

The six positive flows cover a root pod, Alice and Bob on one origin, each with anonymous access
followed by authorization and with proactive authorization. They reach an authenticated tool call
and token refresh. The fixture uses a shared signing key so that its issuer/audience rejection
cases cannot pass solely because pods happen to use different keys. These server checks validate
the fixture model; they do not prove an implementation enforces those boundaries.

**Client validation is incomplete.** The SDK rejects sibling-resource metadata, but accepts a
parent resource, the origin resource and mismatching issuer metadata as far as the authorization
redirect. The output labels all three `CLIENT_LIMITATION`, not `PASS`. A successful process exit
means these recorded observations were reproduced, not that the client satisfies SPS-MCP-035.
An SDK behavior change fails an assertion so that the evidence is reconsidered. Full acceptance
remains open in [#99](https://github.com/sempods/sempods-spec/issues/99).

Run from the repository root with Node 22.19.0, npm and OpenSSL. Installation is temporary; the
specification acquires no npm build or dependency tree. Preserve the generated `package-lock.json`
with the output when recording a run: the SDK is pinned, but npm resolves its transitive ranges at
installation time. Reuse that lock with `npm ci --prefix "$mcp_probe_dir" --ignore-scripts` to
repeat the exact dependency resolution.

```bash
mcp_probe_dir=$(mktemp -d)
npm install --prefix "$mcp_probe_dir" --ignore-scripts --no-audit --no-fund @modelcontextprotocol/sdk@1.30.1
cat > "$mcp_probe_dir/tls.cnf" <<'EOF'
[req]
distinguished_name=dn
x509_extensions=extensions
prompt=no
[dn]
CN=127.0.0.1
[extensions]
subjectAltName=IP:127.0.0.1
basicConstraints=critical,CA:TRUE
keyUsage=critical,digitalSignature,keyCertSign
extendedKeyUsage=serverAuth
EOF
openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
  -keyout "$mcp_probe_dir/key.pem" -out "$mcp_probe_dir/cert.pem" \
  -config "$mcp_probe_dir/tls.cnf"
MCP_SDK_ROOT="$mcp_probe_dir/node_modules/@modelcontextprotocol/sdk" \
MCP_TLS_KEY="$mcp_probe_dir/key.pem" MCP_TLS_CERT="$mcp_probe_dir/cert.pem" \
NODE_EXTRA_CA_CERTS="$mcp_probe_dir/cert.pem" \
  node .github/scripts/probe-mcp-endpoint.mjs > "$mcp_probe_dir/result.json"
cat "$mcp_probe_dir/result.json"
```

The generated key and certificate are temporary fixture material, not deployment credentials.

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
python3 -m pip install rdflib==7.6.0 pyparsing==3.3.2 PyYAML==6.0.3 jsonschema==4.25.1 attrs==26.1.0 jsonschema-specifications==2025.9.1 referencing==0.37.0 rpds-py==2026.6.3 rfc3987-syntax==1.1.0 lark==1.3.1
```

The checker explicitly requires IRI format support at startup. Without that dependency,
`jsonschema` would silently ignore the format and accept invalid identifiers.

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
