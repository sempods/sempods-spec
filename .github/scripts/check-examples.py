#!/usr/bin/env python3
"""Run the worked examples under `examples/` through ACP's own resolution algorithm.

The examples exist so that the access-control concept can be read as scenarios rather than as
argument. That is worth something only while they are true, and prose that restates a contract in
friendlier words is exactly the second copy this repository refuses everywhere else — so the
examples are not prose about the contract, they are **fixtures**, and this script is what makes a
wrong one fail the build instead of misleading a reader.

## What an example is

A scenario file is Markdown with fenced `turtle` blocks carrying a kind in the info string:

    ```turtle acr        an authorization graph; one per resource it controls
    ```turtle context    one attempted access
    ```turtle grant      the access modes that attempt must be granted

Each `context` pairs with the next `grant` below it. A `context` names its `acp:target`, and the
`acr` whose `acp:resource` is that target is the one evaluated. A `grant` block holding only a
comment means nothing is granted — which is a normal outcome and not an error.

Blocks are parsed with a fixed prefix preamble so a reader is not made to scroll past `@prefix`
lines they already know. Each block gets its own base IRI, so `<#owner>` in one block never
collides with `<#owner>` in another.

## Why the algorithm is transcribed rather than imported

`resolve()` below is the pseudocode of ACP §6.1 through §6.5, transcribed and not adapted. That is
the point: sempods claims its access control resources are *pure* ACP — that an independent engine,
given one of them and a context graph, produces the same access grant graph. A checker that shared
sempods' own reading of the vocabulary could not test that claim. This one knows nothing about
sempods.

So a matcher carrying only an attribute ACP does not define — a sempods principal set, say — is
**not satisfied** here, because ACP's rule is that a matcher with none of its four attributes is
never satisfied. That is the correct answer for a foreign engine, and where an example depends on
such an attribute the difference is reported rather than hidden: it is the portability boundary,
and seeing it is the reason to run this.

Usage:

    .github/scripts/check-examples.py             # every scenario under examples/
    .github/scripts/check-examples.py examples/10-owner-only.md
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    from rdflib import Graph, URIRef
except ImportError:  # pragma: no cover - the message is the whole point
    sys.exit(
        "check-examples.py needs rdflib to parse the scenarios.\n\n"
        "    python3 -m pip install rdflib\n\n"
        "It is the specification's first RDF dependency; docs/roadmaps names that as a decision\n"
        "rather than an oversight."
    )

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
INDEX = ROOT / "requirements.json"

ACP = "http://www.w3.org/ns/solid/acp#"
ACL = "http://www.w3.org/ns/auth/acl#"

PREAMBLE = f"@prefix acp: <{ACP}> .\n@prefix acl: <{ACL}> .\n"

BLOCK = re.compile(r"^```turtle[ \t]+(acr|context|grant)[ \t]*$(.*?)^```[ \t]*$", re.M | re.S)
CITATION = re.compile(r"SPS-[A-Z]+-\d{3}")

# The named individuals, spelled out so a typo in a scenario is a mismatch rather than a silent miss.
PUBLIC_AGENT = URIRef(ACP + "PublicAgent")
AUTHENTICATED_AGENT = URIRef(ACP + "AuthenticatedAgent")
CREATOR_AGENT = URIRef(ACP + "CreatorAgent")
OWNER_AGENT = URIRef(ACP + "OwnerAgent")
PUBLIC_CLIENT = URIRef(ACP + "PublicClient")
AUTHENTICATED_CLIENT = URIRef(ACP + "AuthenticatedClient")
PUBLIC_ISSUER = URIRef(ACP + "PublicIssuer")
AUTHENTICATED_ISSUER = URIRef(ACP + "AuthenticatedIssuer")

P = {n: URIRef(ACP + n) for n in (
    "resource", "accessControl", "memberAccessControl", "apply",
    "allow", "deny", "allOf", "anyOf", "noneOf",
    "agent", "client", "issuer", "vc",
    "target", "owner", "creator", "grant",
)}

# Attributes ACP defines for a matcher. Anything else in a matcher is an extension a foreign engine
# does not know, which is worth reporting rather than ignoring.
MATCHER_ATTRIBUTES = {P["agent"], P["client"], P["issuer"], P["vc"]}


@dataclass
class Context:
    """One attempted access, as ACP §3.1 describes it."""

    target: URIRef | None = None
    agent: URIRef | None = None
    client: URIRef | None = None
    issuer: URIRef | None = None
    owners: set = field(default_factory=set)
    creators: set = field(default_factory=set)
    vcs: set = field(default_factory=set)


@dataclass
class Block:
    kind: str
    body: str
    line: int


class Problem(Exception):
    """A scenario that cannot be read at all, as opposed to one whose answer is wrong."""


# --------------------------------------------------------------------------- reading a scenario

def blocks_of(text: str) -> list[Block]:
    return [
        Block(m.group(1), m.group(2), text.count("\n", 0, m.start()) + 1)
        for m in BLOCK.finditer(text)
    ]


def parse(block: Block, index: int) -> Graph:
    """Parse one block, under a base of its own so relative IRIs cannot collide across blocks."""
    graph = Graph()
    try:
        graph.parse(
            data=PREAMBLE + block.body,
            format="turtle",
            publicID=f"https://example.invalid/block/{index}",
        )
    except Exception as exc:
        raise Problem(f"line {block.line}: {block.kind} block is not valid Turtle — {exc}") from exc
    return graph


def one(graph: Graph, subject, predicate, where: str):
    """A context attribute the algorithm reads as single-valued (ACP §6.5.2 does)."""
    values = list(graph.objects(subject, predicate))
    if len(values) > 1:
        raise Problem(
            f"{where}: {predicate} carries {len(values)} values. A context graph may denote a set "
            "of accesses, but a scenario case is one access — split it into separate cases."
        )
    return values[0] if values else None


def read_context(graph: Graph, where: str) -> Context:
    subjects = {s for s, _, _ in graph if (s, P["target"], None) in graph}
    if len(subjects) != 1:
        raise Problem(f"{where}: expected exactly one node carrying acp:target, found {len(subjects)}")
    node = subjects.pop()
    return Context(
        target=one(graph, node, P["target"], where),
        agent=one(graph, node, P["agent"], where),
        client=one(graph, node, P["client"], where),
        issuer=one(graph, node, P["issuer"], where),
        owners=set(graph.objects(node, P["owner"])),
        creators=set(graph.objects(node, P["creator"])),
        vcs=set(graph.objects(node, P["vc"])),
    )


def read_grant(graph: Graph) -> set:
    return set(graph.objects(None, P["grant"]))


# ------------------------------------------------------------------- ACP §6, transcribed as-is

def agent_matches(value, ctx: Context) -> bool:
    if value == PUBLIC_AGENT:
        return True
    if value == AUTHENTICATED_AGENT and ctx.agent is not None:
        return True
    if value == CREATOR_AGENT and ctx.agent is not None and ctx.agent in ctx.creators:
        return True
    if value == OWNER_AGENT and ctx.agent is not None and ctx.agent in ctx.owners:
        return True
    return value == ctx.agent


def client_matches(value, ctx: Context) -> bool:
    if value == PUBLIC_CLIENT:
        return True
    if value == AUTHENTICATED_CLIENT and ctx.client is not None:
        return True
    return value == ctx.client


def issuer_matches(value, ctx: Context) -> bool:
    if value == PUBLIC_ISSUER:
        return True
    if value == AUTHENTICATED_ISSUER and ctx.issuer is not None:
        return True
    return value == ctx.issuer


def satisfied_matcher(graph: Graph, matcher, ctx: Context) -> bool:
    """ACP §6.5: at least one attribute defined, and one value of each defined attribute matching."""
    agents = set(graph.objects(matcher, P["agent"]))
    clients = set(graph.objects(matcher, P["client"]))
    issuers = set(graph.objects(matcher, P["issuer"]))
    vcs = set(graph.objects(matcher, P["vc"]))

    if not (agents or clients or issuers or vcs):
        return False
    if agents and not any(agent_matches(a, ctx) for a in agents):
        return False
    if clients and not any(client_matches(c, ctx) for c in clients):
        return False
    if issuers and not any(issuer_matches(i, ctx) for i in issuers):
        return False
    if vcs and not any(v in ctx.vcs for v in vcs):
        return False
    return True


def satisfied_policy(graph: Graph, policy, ctx: Context) -> bool:
    """ACP §6.4."""
    none_of = list(graph.objects(policy, P["noneOf"]))
    all_of = list(graph.objects(policy, P["allOf"]))
    any_of = list(graph.objects(policy, P["anyOf"]))

    for matcher in none_of:
        if satisfied_matcher(graph, matcher, ctx):
            return False
    for matcher in all_of:
        if not satisfied_matcher(graph, matcher, ctx):
            return False
    for matcher in any_of:
        if satisfied_matcher(graph, matcher, ctx):
            return True
    # No satisfied 'none of', no unsatisfied 'all of', no satisfied 'any of'.
    return len(all_of) != 0 and len(any_of) == 0


def effective_policies(graph: Graph, acr, ancestors: list = ()) -> set:
    """ACP §6.2. Ancestors stay in the signature though no scenario supplies one yet: an ancestor's
    member access controls are how ACP would carry a policy from one target to another, and that is
    the one deviation the concept leaves open."""
    policies = set()
    for control in graph.objects(acr, P["accessControl"]):
        policies.update(graph.objects(control, P["apply"]))
    for ancestor_graph, ancestor in ancestors:
        for control in ancestor_graph.objects(ancestor, P["memberAccessControl"]):
            policies.update(ancestor_graph.objects(control, P["apply"]))
    return policies


def resolve(graph: Graph, acr, ctx: Context) -> set:
    """ACP §6.1 and §6.3: union the allowed modes of satisfied policies, then subtract the denied."""
    allowed, denied = set(), set()
    for policy in effective_policies(graph, acr):
        if satisfied_policy(graph, policy, ctx):
            allowed.update(graph.objects(policy, P["allow"]))
            denied.update(graph.objects(policy, P["deny"]))
    return allowed - denied


# ------------------------------------------------------------------------------ extension notes

def extension_attributes(graph: Graph) -> set:
    """Matcher attributes ACP does not define. Not an error — a portability boundary."""
    found = set()
    for policy_link in (P["allOf"], P["anyOf"], P["noneOf"]):
        for _, _, matcher in graph.triples((None, policy_link, None)):
            for predicate in set(graph.predicates(matcher, None)):
                if str(predicate).startswith(ACP) and predicate not in MATCHER_ATTRIBUTES:
                    continue
                if not str(predicate).startswith(ACP) and predicate != URIRef(
                    "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
                ):
                    found.add(predicate)
    return found


# ------------------------------------------------------------------------------------ the check

def short(term) -> str:
    text = str(term)
    for prefix, short_form in ((ACP, "acp:"), (ACL, "acl:")):
        if text.startswith(prefix):
            return short_form + text[len(prefix):]
    return f"<{text}>"


def check_scenario(path: Path, ids: set[str]) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    notes: list[str] = []
    text = path.read_text(encoding="utf-8")
    # A path outside the repository is legitimate — a scenario can be checked from anywhere while
    # it is being written — so fall back to the path itself rather than failing to name it.
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path

    for citation in sorted(set(CITATION.findall(text))):
        if citation not in ids:
            failures.append(f"{rel}: cites {citation}, which no chapter defines")

    found = blocks_of(text)
    if not found:
        failures.append(f"{rel}: no turtle blocks — a scenario without a case proves nothing")
        return failures, notes

    try:
        by_target: dict = {}
        for index, block in enumerate(b for b in found if b.kind == "acr"):
            graph = parse(block, index)
            for acr, _, target in graph.triples((None, P["resource"], None)):
                by_target[target] = (graph, acr)
            for predicate in extension_attributes(graph):
                notes.append(
                    f"{rel} line {block.line}: matcher uses {short(predicate)}, which ACP does not "
                    "define — a conforming ACP engine leaves that matcher unsatisfied"
                )

        if not by_target:
            failures.append(f"{rel}: no acr block declares acp:resource")
            return failures, notes

        pending = None
        cases = 0
        for offset, block in enumerate(found):
            if block.kind == "context":
                if pending is not None:
                    failures.append(f"{rel} line {pending.line}: context block has no grant block after it")
                pending = block
            elif block.kind == "grant":
                if pending is None:
                    failures.append(f"{rel} line {block.line}: grant block with no context block before it")
                    continue
                where = f"{rel} line {pending.line}"
                ctx = read_context(parse(pending, 1000 + offset), where)
                if ctx.target not in by_target:
                    failures.append(f"{where}: no acr controls {short(ctx.target)}")
                    pending = None
                    continue
                graph, acr = by_target[ctx.target]
                got = resolve(graph, acr, ctx)
                want = read_grant(parse(block, 2000 + offset))
                if got != want:
                    failures.append(
                        f"{where}: expected {{{', '.join(sorted(short(m) for m in want)) or '—'}}}, "
                        f"got {{{', '.join(sorted(short(m) for m in got)) or '—'}}}"
                    )
                cases += 1
                pending = None
        if pending is not None:
            failures.append(f"{rel} line {pending.line}: context block has no grant block after it")
        if cases == 0:
            failures.append(f"{rel}: no context/grant pair")
    except Problem as problem:
        failures.append(f"{rel}: {problem}")

    return failures, notes


def main(argv: list[str]) -> int:
    if not INDEX.exists():
        print(f"{INDEX} is missing; run check-requirements.py --write-index first", file=sys.stderr)
        return 1
    ids = {r["id"] for r in json.loads(INDEX.read_text(encoding="utf-8"))["requirements"]}

    paths = [Path(a).resolve() for a in argv] or sorted(EXAMPLES.glob("*.md"))
    paths = [p for p in paths if p.name != "README.md"]
    if not paths:
        print("no scenarios found under examples/")
        return 0

    failures: list[str] = []
    notes: list[str] = []
    for path in paths:
        scenario_failures, scenario_notes = check_scenario(path, ids)
        failures += scenario_failures
        notes += scenario_notes

    for note in notes:
        print(f"note: {note}")
    if failures:
        print()
        for failure in failures:
            print(f"FAIL {failure}")
        print(f"\n{len(failures)} problem(s) in {len(paths)} scenario(s).")
        return 1

    print(f"{len(paths)} scenario(s) agree with ACP's resolution algorithm.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
