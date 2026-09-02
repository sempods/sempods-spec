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
    ```turtle aside      shown for context, parsed but not evaluated

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

## Misspellings are errors, unknown vocabularies are extensions

A fixture that quietly does nothing is worse than no fixture, because the green run is believed. So
this runner distinguishes two things that look alike. A term from a namespace it knows — `acp:` for
the vocabulary, `acl:` for the modes — that is not a term of that namespace is a **typo**, and it
fails: `acp:agents` on a matcher leaves that matcher unsatisfiable, and a scenario expecting no grant
would otherwise pass for entirely the wrong reason. A term from a namespace it does not know is an
**extension**, and it is reported rather than refused, because that is the portability boundary and
seeing it is the point.

This applies to every predicate in an authorization graph rather than to matchers alone — misspelling
`acp:apply` leaves the policy set empty, which reads as a correct refusal — and to the values as
well: `acp:OwnerAgents` would otherwise pass as an ordinary agent IRI that happens to match nobody.

The same reasoning covers the shapes around them: a block whose kind it cannot read, two access
control resources claiming one target **and one decision kind**, an access control resource nothing
asks about, a policy nothing applies, and an empty run are all failures, because each is a way for
coverage to disappear while the check stays green.

The decision kind is part of that: policy is keyed by the pair — which decision, and which IRI —
because a subject IRI and a context IRI can be the same string, so two access control resources for
one IRI are legitimate exactly when they are two different decisions.

Those guards can rot the same way, so `--self-test` holds each one to a fixture it must reject.

Usage:

    .github/scripts/check-examples.py             # every scenario under examples/
    .github/scripts/check-examples.py examples/10-one-context.md
    .github/scripts/check-examples.py --self-test # the guards still reject what they are for
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    from rdflib import Graph, Literal, URIRef
except ImportError:  # pragma: no cover - the message is the whole point
    sys.exit(
        "check-examples.py needs rdflib to parse the scenarios.\n\n"
        "    python3 -m pip install rdflib==7.6.0 pyparsing==3.3.2\n\n"
        "It is the specification's first RDF dependency; docs/roadmaps names that as a decision\n"
        "rather than an oversight."
    )

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
INDEX = ROOT / "requirements.json"

ACP = "http://www.w3.org/ns/solid/acp#"
ACL = "http://www.w3.org/ns/auth/acl#"

PREAMBLE = f"@prefix acp: <{ACP}> .\n@prefix acl: <{ACL}> .\n"

# `aside` is Turtle a scenario shows without the runner evaluating it — an identity authority's
# membership facts, say, which are not ACP and which no ACP engine has any business resolving. It is
# still parsed, so a malformed one fails; it simply takes no part in a case.
#
# `policy` is one artifact several access control resources reference. Each block otherwise parses
# alone, so a scenario showing two resources under one policy would have to write the policy twice —
# and a green run would then prove two policies that agree, which is the claim's opposite. A policy
# block is merged into every acr graph in the file, so deleting it breaks both cases at once.
#
# `decision` is one request put to *several* access control resources at once, paired with the modes
# the pod grants for it. Each half is still resolved by the plain ACP engine below; what the block
# adds is sempods' composition — both must allow — applied to the answers rather than inside them.
# That rule is the load-bearing claim of the whole model and ACP has no operator for it, so leaving
# it as prose meant a scenario could keep its central sentence while the sentence became false.
#
# `acr-context` and `acr-resource` are the same block, qualified. The lookup key for policy is the
# pair — which decision, and which IRI — and not the IRI alone, because the two dimensions are
# independent: a statement may be *about* a context, so a subject IRI and a context IRI can be the
# same string with two separate decisions on it. Plain `acr` is the unqualified form, for the files
# where only one decision is in play.
# `acr-delegation` is the ceiling: how much of a person's authority an application received. It is
# named rather than inferred, because its target is the principal and a perfectly ordinary resource
# decision can be about the requester's own WebID too.
KINDS = ("acr-context", "acr-resource", "acr-delegation", "acr", "policy", "context", "decision",
         "grant", "aside")
# ` {0,3}` because CommonMark lets a fence be indented that far and still be a fence — a block under
# a list item is the ordinary way it happens. Anchoring at column one would let such a block render
# for a reader and vanish from the runner, which is the failure this file exists to prevent.
# The two fence characters are captured separately so the closing run can be required to use the
# opener's, and to run longer but never shorter. A backreference to a group that did not participate
# cannot match, which is what keeps a backtick block from being closed by tildes.
OPEN = r"(?:(`{3,})|(~{3,}))"
CLOSE = r"^ {0,3}(?:\1`*|\2~*)[ \t]*$"
BLOCK = re.compile(
    r"^ {0,3}" + OPEN + r"[ \t]*turtle[ \t]+(" + "|".join(KINDS) + r")[ \t]*$(.*?)" + CLOSE,
    re.M | re.S,
)
# Any fenced turtle block, so one whose kind is misspelled is reported rather than skipped.
ANY_BLOCK = re.compile(r"^ {0,3}(?:`{3,}|~{3,})[ \t]*turtle([ \t]+[^\n]*)?$", re.M)
# CommonMark renders a fence inside a block quote or a deeply nested list, where the raw line carries
# a container marker. Parsing containers would mean writing a Markdown parser; noticing them costs a
# line, and an unnoticed one is a fixture that renders for a reader and never runs.
CONTAINED = re.compile(
    r"^(?:[ \t>]|[-*+][ \t]|\d+[.)][ \t])*(?:`{3,}|~{3,})[ \t]*turtle([ \t]+[^\n]*)?$", re.M
)
# Every `SPS-` token, not every token that *starts* like one. `SPS-GRANT-0099` has to come out whole
# and fail as unknown rather than matching the real `SPS-GRANT-009` inside it, and `SPS-GRANT-003x`
# has to fail as malformed rather than validating through its valid prefix — a rendered link can show
# the malformed text while pointing at an anchor that resolves, so nothing else would catch it.
CITATION = re.compile(r"(?<![\w-])SPS-[\w-]+|[\w-]+SPS-[\w-]+")
WELL_FORMED = re.compile(r"^SPS-[A-Z]+-\d+$")
# A markdown link whose text is exactly one requirement id, with wherever it actually goes.
MISDIRECTED = re.compile(r"\[`?(SPS-[A-Z]+-\d+)`?\]\(([^)]*)\)")
REFERENCED = re.compile(r"\[`?(SPS-[A-Z]+-\d+)`?\]\[([^\]]*)\]")
# The shortcut form: `[SPS-GRANT-003]` with a definition further down and no second bracket pair.
SHORTCUT = re.compile(r"\[`?(SPS-[A-Z]+-\d+)`?\](?![\[(:])")
REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[([^\]]+)\]:[ \t]*(?:(\S+)|\n[ \t]*(\S+))", re.M)


def normalized(label: str) -> str:
    """A reference label as CommonMark matches one: case-folded, trimmed, runs of space collapsed."""
    return " ".join(label.split()).casefold()

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

# The classes. Nothing here drives resolution — the runner reaches a matcher through acp:anyOf, not
# through its type — but a misspelled `a acp:Policyy` is still a fixture that reads as ACP and is not,
# and a reader believes the type before they trace the links.
POLICY = URIRef(ACP + "Policy")
CLASS_OF = {
    "access control resource": "AccessControlResource", "access control": "AccessControl",
    "policy": "Policy", "matcher": "Matcher",
}
ROLE_OF = {URIRef(ACP + c): name for name, c in CLASS_OF.items()}
KNOWN_CLASSES = {POLICY} | {URIRef(ACP + n) for n in (
    "AccessControlResource", "AccessControl", "Matcher", "Context", "AccessGrant",
)}

# Attributes ACP defines for a matcher. Anything else in a matcher is an extension a foreign engine
# does not know, which is worth reporting rather than ignoring.
MATCHER_ATTRIBUTES = {P["agent"], P["client"], P["issuer"], P["vc"]}

# The named individuals each matcher attribute may carry, kept apart per attribute rather than in one
# set. A value in the ACP namespace outside its attribute's set is a misspelling — `acp:OwnerAgents`
# would fall through as an ordinary agent IRI that happens not to match — and so is a correctly
# spelled individual on the wrong attribute: `acp:client acp:OwnerAgent` reads as deliberate and
# matches nothing, which is a negative case passing for a reason nobody wrote down.
KNOWN_INDIVIDUALS = {
    P["agent"]: {PUBLIC_AGENT, AUTHENTICATED_AGENT, CREATOR_AGENT, OWNER_AGENT},
    P["client"]: {PUBLIC_CLIENT, AUTHENTICATED_CLIENT},
    P["issuer"]: {PUBLIC_ISSUER, AUTHENTICATED_ISSUER},
    P["vc"]: set(),
}


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

# CommonMark's block-level tags. Inside a raw HTML block a fence is text a reader sees as backticks
# rather than a fixture anybody runs — as it is inside an HTML comment, and inside a longer outer
# fence. All three are found by one pass below rather than by matching regions, because a region
# pattern also matches a relative IRI at the start of a Turtle line and would reject a real fixture.
LITERAL_TAGS = ("pre", "script", "style", "textarea")
BLOCK_TAGS = (
    "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|"
    "dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h1|h2|h3|h4|h5|h6|"
    "head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|"
    "p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul"
)
FENCE_LINE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*([^\n]*)$")
LITERAL_OPEN = re.compile(r"^ {0,3}<(" + "|".join(LITERAL_TAGS) + r")\b", re.I)
# CommonMark's other literal raw blocks, each with its own terminator: a processing instruction, a
# declaration, and CDATA. Type 7 — any complete tag alone on its line — closes at a blank line like
# the block tags, and is what carries a custom element.
OTHER_OPEN = ((re.compile(r"^ {0,3}<\?"), "?>"),
              (re.compile(r"^ {0,3}<!\[CDATA\["), "]]>"),
              (re.compile(r"^ {0,3}<![A-Za-z]"), ">"))
LONE_TAG = re.compile(r"^ {0,3}</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>[ \t]*$")
# Lines that are a block of their own rather than paragraph text. A type-7 HTML block cannot
# interrupt a paragraph, but it may follow any of these, so treating every non-blank line as
# paragraph text would hide a fixture that a reader really does see as raw HTML.
PARAGRAPH_BREAK = re.compile(r"^ {0,3}(?:#{1,6}\s|>|[-*+]\s|\d+[.)]\s|\||={2,}\s*$|-{3,}\s*$)|^ {4,}")
BLOCK_OPEN = re.compile(r"^ {0,3}</?(?:" + BLOCK_TAGS + r")\b", re.I)


def scan(text: str) -> tuple[list[str], str]:
    """Fixture fences a reader never sees, which the extractor would still run.

    Three ways to reach that: inside an HTML comment, inside a raw HTML block, and inside a longer
    outer fence. Each renders as nothing or as literal backticks, so the scenario a reader meets and
    the scenario CI checks differ — the one failure this file exists to prevent, from the other side.

    One pass, because the states nest: a `<section>` on a line of Turtle is a relative IRI and not an
    HTML block, and only knowing we are inside a fence tells the two apart.
    """
    problems, seen, rendered = [], set(), []

    def note(where: str) -> None:
        if where not in seen:
            seen.add(where)
            problems.append(f"a turtle fence sits inside {where}, where no reader sees a fixture")

    fence = comment = literal = closer = None
    ordinary = paragraph = False
    for line in text.splitlines():
        opener = FENCE_LINE.match(line)
        turtle = bool(opener) and opener.group(2).strip().startswith("turtle")

        if comment:
            if turtle:
                note("an HTML comment")
            if "-->" in line:
                comment = None
            rendered.append("")
            continue
        if literal:
            if turtle:
                note("a raw HTML block")
            if re.search(rf"</{literal}\s*>", line, re.I):
                literal = None
            rendered.append("")
            continue
        if closer:
            if turtle:
                note("a raw HTML block")
            if closer in line:
                closer = None
            rendered.append("")
            continue
        if ordinary:
            if turtle:
                note("a raw HTML block")
            if not line.strip():
                ordinary = False
            rendered.append("")
            continue
        if fence:
            char, length = fence
            if opener and opener.group(1)[0] == char and len(opener.group(1)) >= length \
                    and not opener.group(2).strip():
                fence = None
            elif turtle:
                note("another fence, where it is literal text")
            rendered.append("")
            continue

        if opener:
            fence = (opener.group(1)[0], len(opener.group(1)))
        elif "<!--" in line and "-->" not in line:
            comment = True
        elif LITERAL_OPEN.match(line):
            tag = LITERAL_OPEN.match(line).group(1)
            # `<pre></pre>` on one line closes where it opens. Leaving the state set would make
            # every fence after it look hidden and reject fixtures a reader can see perfectly well.
            literal = None if re.search(rf"</{tag}\s*>", line, re.I) else tag
        elif BLOCK_OPEN.match(line) or (LONE_TAG.match(line) and not paragraph):
            # A lone tag opens a block only where a paragraph is not already running: CommonMark's
            # type 7 cannot interrupt one, so after prose the tag is inline HTML and the fence below
            # it is an ordinary fence a reader can see.
            ordinary = True
        else:
            for pattern, terminator in OTHER_OPEN:
                if pattern.match(line):
                    closer = None if terminator in line[line.index("<") + 1:] else terminator
                    break
        paragraph = (
            bool(line.strip())
            and not PARAGRAPH_BREAK.match(line)
            and not (fence or comment or literal or closer or ordinary)
        )
        rendered.append("" if fence or comment or literal or closer or ordinary else line)
    return problems, "\n".join(rendered)


def blocks_of(text: str) -> list[Block]:
    return [
        Block(m.group(3), m.group(4), text.count("\n", 0, m.start()) + 1)
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


def requests_in(graph: Graph, where: str) -> set:
    """The nodes describing a request — and nothing else may be in the block.

    Selecting only what carries `acp:target` would leave a second node ignored: it renders for a
    reader, says whatever it likes, and takes no part in any case.
    """
    targeted = {s for s, _, _ in graph if (s, P["target"], None) in graph}
    for node in {s for s, _, _ in graph} - targeted:
        raise Problem(f"{where}: a node in this block carries no acp:target, so nothing reads it")
    return targeted


def read_contexts(graph: Graph, where: str, least: int) -> list[Context]:
    """Every node carrying acp:target, as the halves of one request's decision."""
    subjects = requests_in(graph, where)
    if len(subjects) < least:
        raise Problem(
            f"{where}: expected at least {least} node(s) carrying acp:target, found {len(subjects)}"
        )
    contexts = [read_one_context(graph, node, where) for node in sorted(subjects, key=str)]
    targets = [c.target for c in contexts]
    if len(set(targets)) != len(targets):
        raise Problem(f"{where}: two halves of one decision name the same target")
    # Every half is the same request, or the intersection below composes answers to different
    # questions and means nothing.
    for attribute in ("agent", "client", "issuer"):
        if len({getattr(c, attribute) for c in contexts}) != 1:
            raise Problem(f"{where}: the halves of one decision disagree about acp:{attribute}")
    # Owner and creator are server-derived per target and may legitimately differ. A presented
    # credential is not: it comes with the request, so halves disagreeing about it are two requests,
    # and intersecting their answers certifies an outcome neither of them produces.
    if len({frozenset(c.vcs) for c in contexts}) != 1:
        raise Problem(f"{where}: the halves of one decision present different acp:vc")
    # Ownership is decided against the pod's recorded owner (SPS-AUTH-051), so it is one thing and
    # the same for every target. Letting it vary would let a resource half name the requester and an
    # acp:OwnerAgent policy grant them.
    if len({frozenset(c.owners) for c in contexts}) != 1:
        raise Problem(f"{where}: the halves of one decision disagree about acp:owner")
    return contexts


def read_context(graph: Graph, where: str) -> Context:
    subjects = requests_in(graph, where)
    if len(subjects) != 1:
        raise Problem(f"{where}: expected exactly one node carrying acp:target, found {len(subjects)}")
    return read_one_context(graph, subjects.pop(), where)


# What an access context may say. `acp:allow` is spelled correctly, belongs to ACP, and confers
# nothing here — a fixture carrying it displays request data that looks like a grant.
CONTEXT_PREDICATES = {P[n] for n in ("target", "agent", "client", "issuer", "owner", "creator", "vc")}


def read_one_context(graph: Graph, node, where: str) -> Context:
    errors, _ = classify(graph.predicates(node, None), where, "access context")
    if errors:
        raise Problem(errors[0].split(": ", 1)[1])
    for predicate in set(graph.predicates(node, None)):
        if predicate != RDF_TYPE and predicate not in CONTEXT_PREDICATES:
            raise Problem(f"access context carries {short(predicate)}, which describes no request")
    for value in set(graph.objects(node, RDF_TYPE)):
        if value != URIRef(ACP + "Context"):
            raise Problem(f"access context is typed {short(value)}, not acp:Context")
    # SPS-AUTH-051: ownership is decided against the pod's *recorded* owner, so there is one.
    owners = set(graph.objects(node, P["owner"]))
    if len(owners) > 1:
        raise Problem(f"access context names {len(owners)} owners, and a pod records one")
    for predicate, value in graph.predicate_objects(node):
        if not isinstance(value, URIRef):
            raise Problem(
                f"access context gives {short(predicate)} a literal, and every one of these is an IRI"
            )
    # An access context describes a request: a target, who is asking, which client and issuer. None
    # of those is ever a term ACP defines. Naming one would exploit §6.5.2's last step, which
    # compares the matcher's value to the request's agent after the named individuals have been
    # tried and does not return early — so a request claiming to *be* acp:OwnerAgent satisfies an
    # owner matcher without owning anything. That step is transcribed faithfully below; the fixture
    # that would abuse it is refused here instead.
    # `acp:target` is exempt: a resource decision may control statements about any IRI, ACP's own
    # among them. The other fields are compared to a matcher's values by equality, which is where a
    # request claiming to *be* a reserved individual would satisfy a matcher meant for somebody else.
    for predicate, value in graph.predicate_objects(node):
        if predicate not in (RDF_TYPE, P["target"]) and str(value).startswith(ACP):
            raise Problem(f"access context names {short(value)}, which describes no request")
    return Context(
        target=one(graph, node, P["target"], where),
        agent=one(graph, node, P["agent"], where),
        client=one(graph, node, P["client"], where),
        issuer=one(graph, node, P["issuer"], where),
        owners=set(graph.objects(node, P["owner"])),
        creators=set(graph.objects(node, P["creator"])),
        vcs=set(graph.objects(node, P["vc"])),
    )


def names_a_client(graph: Graph, policy) -> bool:
    """Whether every way of satisfying this policy names one application.

    `acp:allOf` conjoins, so one client-bearing matcher there settles it. `acp:anyOf` is a choice, so
    each alternative has to carry one. A reserved individual is not naming anybody:
    `acp:AuthenticatedClient` admits every application that logged in, and `acp:PublicClient` admits
    the ones that did not.
    """
    def concrete(matcher) -> bool:
        values = set(graph.objects(matcher, P["client"]))
        # Values of one attribute are alternatives, so a reserved one beside a named application
        # widens rather than narrows: every authenticated client satisfies the matcher anyway.
        if values & {PUBLIC_CLIENT, AUTHENTICATED_CLIENT}:
            return False
        return any(isinstance(v, URIRef) for v in values)

    if any(concrete(m) for m in graph.objects(policy, P["allOf"])):
        return True
    alternatives = list(graph.objects(policy, P["anyOf"]))
    return bool(alternatives) and all(concrete(m) for m in alternatives)


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

RDF_TYPE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

# Everything ACP defines that may legitimately appear as a predicate in a fixture. A predicate in the
# ACP namespace outside this set is a misspelling, not a feature.
KNOWN_ACP = set(P.values()) | {URIRef(ACP + "attribute")}

# The modes WAC defines. One in the acl: namespace outside this set is a misspelling; the sempods
# context mode will live in a namespace of its own and is reported as an extension until it is named.
KNOWN_ACL = {URIRef(ACL + n) for n in ("Read", "Write", "Append", "Control")}

# The three the profile maps sempods' permissions onto. `acl:Append` is spelled correctly and is
# still not one of them — SPS-GRANT-006 has read, write and manage and nothing between write and
# read — so a fixture using it is certifying an authority sempods cannot grant.
ACL_READ, ACL_WRITE, ACL_CONTROL = (URIRef(ACL + n) for n in ("Read", "Write", "Control"))
PROFILE_MODES = {ACL_READ, ACL_WRITE, ACL_CONTROL}


def classify(predicates, where: str, on: str) -> tuple[list[str], set]:
    """Split predicates into misspellings of a known vocabulary and terms of an unknown one."""
    errors, extensions = [], set()
    for predicate in predicates:
        if predicate == RDF_TYPE or predicate in KNOWN_ACP:
            continue
        if str(predicate).startswith(ACP):
            errors.append(f"{where}: {on} carries {short(predicate)}, which ACP does not define")
        else:
            extensions.add(predicate)
    return errors, extensions


def inspect_acr(graph: Graph, where: str) -> tuple[list[str], list[str]]:
    """Every predicate in an authorization graph, and every matcher value.

    Not only matcher nodes: misspelling `acp:apply` as `acp:applies` leaves the policy set empty, so
    a negative case would pass while the graph said nothing at all.
    """
    errors, extensions = classify(set(graph.predicates(None, None)), where, "authorization graph")
    matcher_nodes = set()
    for link in (P["allOf"], P["anyOf"], P["noneOf"]):
        matcher_nodes |= set(graph.objects(None, link))
    notes = []
    for predicate in extensions:
        # On a matcher the note is true and is the portability boundary. Anywhere else the resolver
        # simply ignores the predicate, so the same note would report a condition as fail-closed
        # while it does nothing at all — and a fixture carrying an inert condition is claiming one.
        if set(graph.subjects(predicate, None)) <= matcher_nodes:
            notes.append(
                f"{where}: uses {short(predicate)}, which ACP does not define — a conforming ACP "
                "engine leaves a matcher carrying it unsatisfied"
            )
        else:
            errors.append(
                f"{where}: {short(predicate)} is outside a matcher, where an ACP engine ignores it "
                "rather than failing closed"
            )
    # The resolver below implements these, deliberately: it is an ACP engine and has to answer for
    # graphs the profile would not write. A *fixture* carrying one is a different thing — it would
    # certify an access control resource outside the model these files demonstrate.
    for predicate in (P["deny"], P["noneOf"], P["memberAccessControl"]):
        if (None, predicate, None) in graph:
            errors.append(
                f"{where}: uses {short(predicate)}, which the sempods profile excludes"
            )
    for value in set(graph.objects(None, RDF_TYPE)):
        if str(value).startswith(ACP) and value not in KNOWN_CLASSES:
            errors.append(f"{where}: types a node acp:{str(value)[len(ACP):]}, which ACP has no class for")
    for attribute, individuals in KNOWN_INDIVIDUALS.items():
        for value in set(graph.objects(None, attribute)):
            # SPS-AUTH-049: a pod knows a person only as a WebID URI. A literal on both the matcher
            # and the request compares equal to itself, so the case passes on an identity the
            # specification refuses to hold.
            if not isinstance(value, URIRef):
                errors.append(
                    f"{short(attribute)} names a literal, and an identity is an IRI "
                    f"(SPS-AUTH-049) — at {where}"
                )
                continue
            if str(value).startswith(ACP) and value not in individuals:
                errors.append(
                    f"{where}: {short(attribute)} names {short(value)}, which is not one of the "
                    "individuals ACP defines for it"
                )
    # A predicate ACP defines, on a node it does not describe. `acp:apply` written straight onto the
    # access control resource rather than beneath `acp:accessControl` is spelled correctly, reads as
    # a policy reference, and leaves the policy set empty — so a case expecting no grant stays green
    # over a graph that says nothing. Roles are read off the links, which is how ACP §6 finds them.
    #
    # A node holds a role if something links to it in that position *or* if it says so with its type.
    # The type half is not decoration: a shared `policy` block is merged into every access control
    # resource in the file, so in all but the ones that apply it nothing links to it at all.
    for link in (P["accessControl"], P["memberAccessControl"], P["apply"],
                 P["allOf"], P["anyOf"], P["noneOf"]):
        for value in set(graph.objects(None, link)):
            if isinstance(value, Literal):
                errors.append(
                    f"{where}: {short(link)} points at the literal \"{value}\" — later lookups find "
                    "no triples for it, which is the silence this runner exists to break"
                )
            elif str(value).startswith(ACP):
                # A policy or matcher is the fixture's own IRI or a blank node, never a term ACP
                # defines. `acp:apply acp:Polciy` reads as a reserved name and is a misspelling; give
                # it policy triples and role inference believes it.
                errors.append(
                    f"{where}: {short(link)} points at {short(value)}, and ACP's own terms are not "
                    "policies or matchers"
                )
            elif value not in set(graph.subjects(None, None)):
                errors.append(
                    f"{where}: {short(link)} points at {short(value)}, which the graph says nothing "
                    "about — resolution finds no modes and no attributes there"
                )

    # 2 — a predicate belonging to another kind of block
    if (None, URIRef(ACP + "attribute"), None) in graph:
        errors.append(
            f"{where}: uses acp:attribute, which is the super-property rather than an attribute — "
            "§6.5 reads the four ACP names, so a matcher carrying it is satisfied by nobody and the "
            "condition it displays is evaluated by no one"
        )
    for predicate in (P["target"], P["owner"], P["creator"], P["grant"]):
        if (None, predicate, None) in graph:
            errors.append(
                f"{where}: carries {short(predicate)}, which belongs to a context or grant block "
                "and takes no part in an authorization graph"
            )

    def typed(name: str) -> set:
        return set(graph.subjects(RDF_TYPE, URIRef(ACP + name)))

    linked = {
        "access control resource": set(graph.subjects(P["resource"], None)),
        "access control": set(graph.objects(None, P["accessControl"]))
        | set(graph.objects(None, P["memberAccessControl"])),
        "policy": set(graph.objects(None, P["apply"])),
        "matcher": set(graph.objects(None, P["allOf"]))
        | set(graph.objects(None, P["anyOf"]))
        | set(graph.objects(None, P["noneOf"])),
    }
    roles = {name: nodes | typed(CLASS_OF[name]) for name, nodes in linked.items()}

    # A class the graph knows, on a node the links put somewhere else. Typing a linked policy
    # `a acp:AccessControl` resolves and passes, because acp:apply gives it the policy role
    # regardless — so the fixture renders an ACP shape that is not one.
    reached = set().union(*linked.values())
    for node, _, value in graph.triples((None, RDF_TYPE, None)):
        if not isinstance(value, URIRef):
            errors.append(f"{where}: types a node with the literal \"{value}\", not a class")
            continue
        if not str(value).startswith(ACP):
            # `[ a ex:Condition ]` renders as a condition, is exempt from predicate classification
            # because it is an rdf:type, and is outside every ACP role — so nothing else looks at it.
            if node not in reached:
                errors.append(
                    f"{where}: {short(value)} types a node no link reaches, so ACP never sees it"
                )
            continue
        declared = ROLE_OF.get(value)
        if declared is None:
            errors.append(
                f"{where}: types a node {short(value)}, which describes no part of an "
                "authorization graph"
            )
            continue
        for name, nodes in linked.items():
            if node in nodes and name != declared:
                errors.append(
                    f"{where}: a node the links make {name} is typed {short(value)}"
                )
    belongs = {
        P["resource"]: "access control resource",
        P["accessControl"]: "access control resource",
        P["memberAccessControl"]: "access control resource",
        P["apply"]: "access control",
        P["allow"]: "policy", P["deny"]: "policy",
        P["allOf"]: "policy", P["anyOf"]: "policy", P["noneOf"]: "policy",
        P["agent"]: "matcher", P["client"]: "matcher",
        P["issuer"]: "matcher", P["vc"]: "matcher",
    }
    for predicate, role in belongs.items():
        for subject in set(graph.subjects(predicate, None)):
            if subject not in roles[role]:
                errors.append(
                    f"{where}: {short(predicate)} is on a node that is no {role}, so nothing reaches it"
                )
    # Per policy, because a set collected across the graph lets one policy's acl:Read stand in for
    # another's missing one. ACP carries no implication of its own, so a policy saying acl:Write and
    # not acl:Read grants exactly that to any engine reading it — the profile expands when the policy
    # is written, and here is where the writing is checked.
    for policy in roles["policy"]:
        modes = set(graph.objects(policy, P["allow"]))
        for mode, implied in ((ACL_WRITE, {ACL_READ}), (ACL_CONTROL, {ACL_READ, ACL_WRITE})):
            missing = implied - modes if mode in modes else set()
            if missing:
                errors.append(
                    f"{where}: a policy allows {short(mode)} without "
                    + ", ".join(sorted(short(m) for m in missing))
                    + " — the profile expands when the policy is written"
                )
        # The public matcher is permitted for read and nothing else. Under acp:allOf it happens to
        # be harmless and also pointless, since it is satisfied by every request; refusing it there
        # too costs nothing and keeps the rule the one sentence the profile states.
        matchers = set(graph.objects(policy, P["allOf"])) | set(graph.objects(policy, P["anyOf"]))
        # Every reserved individual an unauthenticated request satisfies, not just the agent one:
        # a matcher carrying only acp:client acp:PublicClient is satisfied by a request with no
        # client and no agent at all, so a policy behind it grants anonymously.
        public = any(
            value in (PUBLIC_AGENT, PUBLIC_CLIENT, PUBLIC_ISSUER)
            for m in matchers
            for attribute in (P["agent"], P["client"], P["issuer"])
            for value in graph.objects(m, attribute)
        )
        if public and modes - {ACL_READ}:
            errors.append(
                f"{where}: a policy reaching acp:PublicAgent allows "
                + ", ".join(sorted(short(m) for m in modes - {ACL_READ}))
                + " — the profile permits the public matcher for read only"
            )
    # A matcher mixing an extension attribute with one of ACP's is the one construction where a
    # foreign engine answers *more*: ACP conjoins the attribute types within a matcher, and an
    # engine that cannot see the extension has one conjunct fewer to fail. The profile forbids it —
    # the conjunction goes in two matchers under acp:allOf — and here is where that is enforced.
    for link in (P["allOf"], P["anyOf"], P["noneOf"]):
        for _, _, matcher in graph.triples((None, link, None)):
            predicates = set(graph.predicates(matcher, None))
            native = predicates & MATCHER_ATTRIBUTES
            foreign = {p for p in predicates if not str(p).startswith(ACP) and p != RDF_TYPE}
            if native and foreign:
                errors.append(
                    f"{where}: a matcher carries {short(sorted(native, key=str)[0])} beside "
                    f"{short(sorted(foreign, key=str)[0])} — an engine that cannot see the second "
                    "grants on the first alone, so write the conjunction as two acp:allOf matchers"
                )
    return errors, notes


def inspect_grant(graph: Graph, where: str) -> list[str]:
    """A grant block states granted modes and nothing else.

    Its `rdf:type` is checked here rather than left exempt: a grant graph never reaches the class
    validation an authorization graph gets, so `a acp:AccessGrannt` would compare equal to the
    expectation and certify a misspelling in ACP's own namespace.
    """
    errors = [
        f"{where}: grant block carries {short(predicate)}, not acp:grant"
        for predicate in set(graph.predicates(None, None))
        if predicate not in (P["grant"], RDF_TYPE)
    ]
    errors += [
        f"{where}: a node in this grant block carries no acp:grant, so it says nothing"
        for subject in set(graph.subjects(None, None))
        if (subject, P["grant"], None) not in graph
    ]
    return errors + [
        f"{where}: grant block is typed {short(value)}, not acp:AccessGrant"
        for value in set(graph.objects(None, RDF_TYPE))
        if value != URIRef(ACP + "AccessGrant")
    ]


def inspect_modes(terms, where: str, on: str, notes: list | None = None) -> list[str]:
    """A mode in the acl: namespace that WAC does not define is a typo; one WAC defines and the
    profile does not is a mode sempods has no permission for."""
    errors = []
    notes = notes if notes is not None else []
    for term in terms:
        # Before anything about namespaces: `acp:allow "acl:Read"` looks right, reads as a mode, and
        # is a string. Used the same way in the policy and the expectation it compares equal to
        # itself, so the case passes over a graph that grants nothing.
        if not isinstance(term, URIRef):
            shown = f'"{term}"' if isinstance(term, Literal) else "a blank node"
            errors.append(f"{where}: {on} names {shown}, and a mode is an IRI")
            continue
        if str(term).startswith(ACP):
            # `acp:Raed` reads as a reserved name; used in the policy and the expectation alike it
            # compares equal to itself. ACP defines no access modes at all (§5.2).
            errors.append(f"{where}: {on} names {short(term)}, and ACP defines no access modes")
            continue
        if not str(term).startswith(ACL):
            # Not a typo and not a mode this profile knows — the sempods context term will look like
            # this once it is named, so it is reported rather than refused.
            notes.append(
                f"{where}: {on} names {short(term)}, which is neither an ACL mode nor one the "
                "sempods profile has named yet"
            )
            continue
        if term not in KNOWN_ACL:
            errors.append(f"{where}: {on} names {short(term)}, which is not an ACL access mode")
        elif term not in PROFILE_MODES:
            errors.append(
                f"{where}: {on} names {short(term)}, which sempods has no permission for — "
                "SPS-GRANT-006 has read, write and manage and nothing between read and write"
            )
    return errors


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

    # A link showing one requirement and ending at another passes both checks that exist: the text
    # names a real id, and the anchor resolves. Only the pair is wrong, and only a reader sees it.
    # Links and reference definitions are Markdown, so only what Markdown renders is one: a
    # definition inside a code fence is inert text, and taking it as the first definition would
    # excuse the real one below it.
    problems, prose = scan(text)

    definitions: dict = {}
    # The first wins, as CommonMark resolves it. Keeping the last would validate a correct
    # destination while the rendered link followed an earlier, wrong one.
    for label, same_line, next_line in REFERENCE_DEFINITION.findall(prose):
        definitions.setdefault(normalized(label), same_line or next_line)
    citations = [(shown, dest) for shown, dest in MISDIRECTED.findall(prose)]
    for shown in SHORTCUT.findall(prose):
        if normalized(shown) in definitions:
            citations.append((shown, definitions[normalized(shown)]))
    for shown, label in REFERENCED.findall(prose):
        # `[SPS-GRANT-003][wrong]` names a real id and resolves to a real anchor, so both existing
        # checks are satisfied and only the pairing is wrong. `[id][]` points at its own text.
        citations.append((shown, definitions.get(normalized(label or shown), "")))
    for shown, destination in citations:
        anchor = destination.partition("#")[2]
        if anchor != shown:
            failures.append(
                f"{rel}: a link showing {shown} ends at "
                + (f"#{anchor}" if anchor else "the chapter rather than the requirement")
            )

    for citation in sorted(set(CITATION.findall(text))):
        if not WELL_FORMED.match(citation):
            failures.append(f"{rel}: writes {citation}, which is not the shape of a requirement id")
        elif citation not in ids:
            failures.append(f"{rel}: cites {citation}, which no chapter defines")

    found = blocks_of(text)
    # A block whose kind is misspelled matches no pattern above and would simply vanish, taking its
    # case with it while the rest of the file still passes.
    for problem in problems:
        failures.append(f"{rel}: {problem}")
    if len(CONTAINED.findall(text)) != len(ANY_BLOCK.findall(text)):
        failures.append(
            f"{rel}: a turtle fence sits inside a block quote or a nested list, where it renders "
            "for a reader and is never evaluated — put it at the top level"
        )
    if len(ANY_BLOCK.findall(text)) != len(found):
        failures.append(
            f"{rel}: a fenced turtle block carries a kind that is not one of {', '.join(KINDS)}"
        )
    if not found:
        failures.append(f"{rel}: no turtle blocks — a scenario without a case proves nothing")
        return failures, notes

    try:
        # One graph, referenced from every access control resource below — the artifact itself,
        # rather than a copy per reference.
        shared = Graph()
        for index, block in enumerate(b for b in found if b.kind == "policy"):
            artifact = parse(block, 4000 + index)
            # A shared block is merged into every access control resource in the file, so an access
            # control resource smuggled into one would be registered as a decision of its own while
            # being displayed under the wrong kind.
            for name in ("AccessControlResource", "AccessControl"):
                if (None, RDF_TYPE, URIRef(ACP + name)) in artifact:
                    failures.append(
                        f"{rel} line {block.line}: a policy block types a node acp:{name}, and a "
                        "shared artifact is a policy and its matchers"
                    )
            for predicate in (P["resource"], P["accessControl"], P["memberAccessControl"]):
                if (None, predicate, None) in artifact:
                    failures.append(
                        f"{rel} line {block.line}: a policy block carries {short(predicate)}, and a "
                        "shared artifact is a policy and its matchers"
                    )
            shared += artifact
            shared_errors, shared_notes = inspect_acr(shared, f"{rel} line {block.line}")
            failures += shared_errors
            notes += shared_notes

        shared_subjects = set(shared.subjects(None, None))
        shared_policies = shared_subjects
        by_target: dict = {}
        applied: set = set()
        for index, block in enumerate(b for b in found if b.kind.startswith("acr")):
            kind = block.kind[4:] or "unqualified"
            own, acr = parse(block, index), None
            # Adding triples to a shared policy's subject makes a private version of it for this
            # access control resource only — one edit reaching every referrer is the claim these
            # files make, and two versions that differ is that claim being false.
            for subject in set(own.subjects(None, None)) & shared_subjects:
                failures.append(
                    f"{rel} line {block.line}: says more about {short(subject)}, which a policy "
                    "block owns — a shared artifact has one version"
                )
            graph = own + shared
            where = f"{rel} line {block.line}"
            # Walked from the access control resource rather than read off the graph: a typed but
            # unlinked acp:AccessControl carrying acp:apply would otherwise mark a shared policy
            # exercised that resolve() can never reach.
            for acr_node in set(graph.subjects(P["resource"], None)):
                for control in set(graph.objects(acr_node, P["accessControl"])) | set(
                    graph.objects(acr_node, P["memberAccessControl"])
                ):
                    applied |= set(graph.objects(control, P["apply"]))
            # Without this, a block declaring no target adds nothing to by_target and no later check
            # can see it: the file passes on its other blocks while this one is never evaluated.
            subjects = set(own.subjects(P["resource"], None)) | set(
                own.subjects(RDF_TYPE, URIRef(ACP + "AccessControlResource"))
            )
            targets = set(own.objects(None, P["resource"]))
            # Both counts, because either alone lets the other slip: a second, targetless access
            # control resource beside a correct one leaves `targets` at exactly one, and everything
            # it applies is never resolved.
            for target in targets:
                if not isinstance(target, URIRef):
                    failures.append(
                        f"{where}: acp:resource carries the literal \"{target}\", and a target is an IRI"
                    )
            if len(subjects) != 1 or len(targets) != 1:
                failures.append(
                    f"{where}: an acr block holds {len(subjects)} access control resource(s) and "
                    f"{len(targets)} target(s), and the profile makes one canonical for one"
                )
            for acr, _, target in graph.triples((None, P["resource"], None)):  # noqa: B020
                kinds = {k for k, _, _ in by_target.get(target, ())}
                # Two decisions on one IRI are the context one and the resource one. An unqualified
                # block beside a qualified one would make a third, and modes_for() would intersect
                # all of them — a fixture modelling something the concept does not describe.
                if kinds and ("unqualified" in kinds) != (kind == "unqualified"):
                    failures.append(
                        f"{where}: {short(target)} is claimed by both a qualified and an "
                        "unqualified acr, and the pair is context and resource"
                    )
                if any(k == kind for k, _, _ in by_target.get(target, ())):
                    # Silently replacing the first mapping would leave its policies never evaluated.
                    # Two decisions on one IRI are legitimate; two of the same kind are not.
                    failures.append(f"{where}: a second {kind} acr claims {short(target)}")
                by_target.setdefault(target, []).append((kind, graph, acr))
            acr_errors, acr_notes = inspect_acr(graph, where)
            failures += acr_errors
            notes += acr_notes
            if acr is None:
                # The shape failure above says why. Walking from an access control resource that is
                # not there would raise instead of reporting it, and take the other scenarios with
                # it — a crash in the checker is the loudest possible way to check nothing.
                continue
            # This access control resource's own policies, not the graph's: a shared policy is
            # merged into every one of them, so a graph-wide sweep would blame this decision for a
            # mode only some other decision applies.
            applies = set()
            for control in set(graph.objects(acr, P["accessControl"])) | set(
                graph.objects(acr, P["memberAccessControl"])
            ):
                applies |= set(graph.objects(control, P["apply"]))
            modes = {m for policy in applies
                     for link in (P["allow"], P["deny"])
                     for m in graph.objects(policy, link)}
            # A ceiling speaks about a pair — this person through this application. Read off the
            # shape rather than probed: a probe answers for the one request it describes, so a
            # policy requiring an issuer the probe omits would pass while the real request grants to
            # every client. It has to be unsatisfiable without a named application, whatever else a
            # request carries.
            if kind == "delegation":
                for policy in applies:
                    if not names_a_client(graph, policy):
                        failures.append(
                            f"{where}: a delegation policy has a path that grants without naming an "
                            "application — a ceiling names the client the person authorized"
                        )
            failures += inspect_modes(modes, where, "policy", notes)
            # `acl:Control` is reading and writing an access control resource. Context management
            # also creates and deletes contexts and reaches slash-delimited descendants, so the
            # profile gives it a sempods term of its own — which is not named yet, and until it is
            # a context policy cannot spell `manage` at all.
            # A ceiling may carry it too: bounding an application's *resource* management means
            # spelling out what resource management is.
            if ACL_CONTROL in modes and kind not in ("resource", "delegation"):
                failures.append(
                    f"{where}: allows acl:Control outside an acr-resource or acr-delegation block. "
                    "It is management of an access control resource; context management also "
                    "creates, deletes and reaches descendants, and has a sempods term of its own "
                    "that is not named yet"
                )

        # An inline policy nothing applies is the same silence as an unapplied shared one, and it
        # sits inside a graph whose other policy can carry every case in the file.
        for kind, graph, acr in [e for entries in by_target.values() for e in entries]:
            reachable = set()
            for control in set(graph.objects(acr, P["accessControl"])) | set(
                graph.objects(acr, P["memberAccessControl"])
            ):
                reachable |= set(graph.objects(control, P["apply"]))
            candidates = set(graph.objects(None, P["apply"])) | set(graph.subjects(RDF_TYPE, POLICY))
            for policy in sorted(candidates - reachable, key=str):
                # Reachability is per graph. `applied` is the whole file, and letting it excuse an
                # inline policy would mean another block naming the same absolute IRI suppresses
                # this one — whose own triples resolution never reads. Only a policy that came from
                # a shared block is genuinely covered elsewhere.
                if policy not in shared_policies:
                    failures.append(f"{rel}: nothing applies {short(policy)}")
            # The same silence one level further down: a typed matcher no policy links to renders
            # as a condition and takes no part in any case.
            linked = set()
            for link in (P["allOf"], P["anyOf"], P["noneOf"]):
                linked |= set(graph.objects(None, link))
            for matcher in sorted(set(graph.subjects(RDF_TYPE, URIRef(ACP + "Matcher"))) - linked,
                                  key=str):
                failures.append(f"{rel}: no policy references {short(matcher)}")
            controls = set(graph.objects(acr, P["accessControl"])) | set(
                graph.objects(acr, P["memberAccessControl"])
            )
            for control in sorted(
                set(graph.subjects(RDF_TYPE, URIRef(ACP + "AccessControl"))) - controls, key=str
            ):
                failures.append(f"{rel}: no access control resource holds {short(control)}")

        if not by_target:
            failures.append(f"{rel}: no acr block declares acp:resource")
            return failures, notes

        # Parsed for well-formedness and then set aside: a malformed one still fails.
        for index, block in enumerate(b for b in found if b.kind == "aside"):
            parse(block, 3000 + index)

        pending = None
        cases = 0
        exercised: set = set()

        def reachable_anonymously(graph: Graph, acr, target) -> bool:
            """Whether an unauthenticated request gets anything here.

            Asked by resolving rather than by looking for a public token: a matcher combining
            `acp:PublicAgent` with `acp:AuthenticatedClient` carries one and is satisfied by nobody
            anonymous, and treating it as a public branch would refuse a fixture that is fine.
            """
            return bool(resolve(graph, acr, Context(target=target)))

        def modes_for(ctx: Context, where: str, composed: bool = False,
                      ceiling: bool = False) -> set | None:
            if ctx.target not in by_target:
                failures.append(f"{where}: no acr controls {short(ctx.target)}")
                return None
            # Every decision keyed to this IRI, intersected: where a subject is also a context, both
            # apply to the one request and the finer one can only subtract.
            entries = by_target[ctx.target]
            # Both apply when the request *is* about this IRI — the subject-equals-context case,
            # written as a lone context block. As one half of a decision about something else, the
            # half means the context decision or the resource decision and cannot say which, so the
            # runner refuses rather than narrowing by an unrelated policy.
            if len(entries) > 1 and composed:
                failures.append(
                    f"{where}: {short(ctx.target)} carries two decisions, so a half of a larger "
                    "decision cannot say which of them it means"
                )
                return None
            answers = []
            for kind, graph, acr in entries:
                exercised.add((kind, ctx.target))
                answers.append(resolve(graph, acr, ctx))
            return set.intersection(*answers)
        for offset, block in enumerate(found):
            if block.kind in ("context", "decision"):
                if pending is not None:
                    failures.append(
                        f"{rel} line {pending.line}: {pending.kind} block has no grant block after it"
                    )
                pending = block
            elif block.kind == "grant":
                if pending is None:
                    failures.append(f"{rel} line {block.line}: grant block with no context block before it")
                    continue
                where = f"{rel} line {pending.line}"
                # A `context` block holding two nodes would be silently composed like a `decision`,
                # which is a different claim: the expectation would match an intersection nobody
                # wrote. So the two kinds are read with different arities.
                halves = (read_contexts(parse(pending, 1000 + offset), where, least=2)
                          if pending.kind == "decision"
                          else [read_context(parse(pending, 1000 + offset), where)])
                # 4 — a composed decision has the dimensions the model has: the context every pod
                # decides, at most one finer decision on the resource, at most one ceiling. Two
                # context halves would compose decisions no single statement is subject to, and a
                # composition without one would skip the sandbox every pod enforces.
                # 3 — and the ceiling bounds the principal it names, so its half is about them.
                dimensions: list = []
                composed = len(halves) > 1
                for half in halves:
                    for k, _, _ in by_target.get(half.target, ()):
                        dimensions.append(k)
                        if k == "delegation" and half.target != half.agent:
                            failures.append(
                                f"{where}: a delegation half targets {short(half.target)} while the "
                                f"request is {short(half.agent)} — a ceiling bounds the principal "
                                "it names"
                            )
                # The concept applies the ceiling to authenticated authority and then unions the
                # public branch, while this block intersects uniformly — the same answer everywhere
                # except where a public branch exists. It exists only if *every* narrowing half
                # admits an anonymous read, so that is what is asked, rather than whether any single
                # half happens to be public.
                bounds = "delegation" in dimensions
                if bounds:
                    anonymous = [
                        resolve(graph, acr, Context(target=half.target))
                        for half in halves
                        for k, graph, acr in by_target.get(half.target, ())
                        if k != "delegation"
                    ]
                    if anonymous and ACL_READ in set.intersection(*anonymous):
                        failures.append(
                            f"{where}: composes a delegation ceiling with a target every half opens "
                            "to anonymous read, and the public branch unions where this block "
                            "intersects — write the halves that narrow, and read the ceiling off "
                            "the authenticated case"
                        )
                        pending = None
                        continue
                if composed:
                    for kind_name, allowed in (("context", 1), ("resource", 1), ("delegation", 1),
                                               ("unqualified", 0)):
                        if dimensions.count(kind_name) > allowed:
                            failures.append(
                                f"{where}: composes {dimensions.count(kind_name)} {kind_name} "
                                f"decisions, and the model has at most {allowed}"
                            )
                    if "context" not in dimensions:
                        failures.append(
                            f"{where}: composes no context decision, and every access passes the "
                            "context it is in first"
                        )
                answers = [
                    modes_for(ctx, where, composed=composed, ceiling=bounds) for ctx in halves
                ]
                if any(a is None for a in answers):
                    pending = None
                    continue
                # sempods' rule, and deliberately here rather than in the engine: each answer above
                # is what any ACP engine produces, and the intersection is what the pod does with
                # them. A union would let a resource policy widen what a context refused.
                got = set.intersection(*answers)
                grant_graph = parse(block, 2000 + offset)
                failures += inspect_grant(grant_graph, f"{rel} line {block.line}")
                want = read_grant(grant_graph)
                failures += inspect_modes(want, f"{rel} line {block.line}", "grant", notes)
                if got != want:
                    failures.append(
                        f"{where}: expected {{{', '.join(sorted(short(m) for m in want)) or '—'}}}, "
                        f"got {{{', '.join(sorted(short(m) for m in got)) or '—'}}}"
                    )
                cases += 1
                pending = None
        if pending is not None:
            failures.append(
                f"{rel} line {pending.line}: {pending.kind} block has no grant block after it"
            )
        if cases == 0:
            failures.append(f"{rel}: no context/grant pair")
        # An access control resource nothing asks about is prose, not a case: it could say anything
        # and the file would still pass.
        declared = {(kind, target) for target, entries in by_target.items() for kind, _, _ in entries}
        for kind, target in sorted(declared - exercised, key=str):
            failures.append(
                f"{rel}: nothing asks about {short(target)}, so its {kind} acr is never evaluated"
            )
        # A shared policy nothing applies is the same silence one level up.
        for policy in sorted(set(shared.subjects(RDF_TYPE, POLICY)) - applied, key=str):
            failures.append(f"{rel}: no acr applies {short(policy)}")
    except Problem as problem:
        failures.append(f"{rel}: {problem}")

    return failures, notes


# ------------------------------------------------------------------------------------- self-test
#
# Every check above exists because a fixture could be wrong in that particular way and still pass.
# A check that stops firing brings the silence back without failing anything, so each one is held
# to a case it must reject. The fixtures live here rather than under `examples/`, where the default
# glob would pick them up and the regular run would break on purpose.

SOUND = """
```turtle acr
[ a acp:AccessControlResource ;
  acp:resource <https://a.example/c> ;
  acp:accessControl [ acp:apply <#p> ] ] .
<#p> a acp:Policy ; acp:allow acl:Read ;
     acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .
```
```turtle context
[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .
```
```turtle grant
[] acp:grant acl:Read .
```
"""

# Each: what is broken, the substitution that breaks it, and the wording that must name it. The last
# two resolve to the expected grant regardless — the fall-through is the whole point of checking.
BROKEN = [
    ("a misspelled predicate on the access control resource",
     ("acp:accessControl [", "acp:accessControls ["), "acp:accessControls"),
    ("a misspelled predicate inside a policy",
     ("acp:anyOf [", "acp:anyOfs ["), "acp:anyOfs"),
    ("a turtle block whose kind is misspelled",
     ("```turtle grant", "```turtle grants"), "kind that is not one of"),
    ("a misspelled ACP individual, which would pass as an ordinary IRI",
     ("<https://b.example/#me>", "acp:OwnerAgents"), "acp:OwnerAgents"),
    ("a misspelled predicate in a grant block",
     ("[] acp:grant acl:Read .", "[] acp:grants acl:Read ."), "not acp:grant"),
    ("an access control resource nothing asks about",
     ("acp:resource <https://a.example/c> ;",
      "acp:resource <https://a.example/c>, <https://a.example/unused> ;"), "never evaluated"),
    ("a misspelled ACP class",
     ("a acp:Policy ;", "a acp:Policyy ;"), "no class for"),
    ("a shared policy no access control resource applies",
     ("```turtle context", "```turtle policy\n<https://a.example/spare> a acp:Policy ; "
      "acp:allow acl:Read .\n```\n```turtle context"), "no acr applies"),
    ("a known predicate on a node that is no policy",
     ("acp:accessControl [ acp:apply <#p> ] ] .", "acp:apply <#p> ] .")," is no access control"),
    ("an acr block declaring no target at all",
     ("```turtle context", "```turtle acr\n<#stray> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n```\n```turtle context"),
     "access control resource(s) and 0 target(s)"),
    ("a second, targetless access control resource beside a correct one",
     ("acp:accessControl [ acp:apply <#p> ] ] .",
      "acp:accessControl [ acp:apply <#p> ] ] .\n"
      "[ a acp:AccessControlResource ; acp:accessControl [ acp:apply <#q> ] ] .\n"
      "<#q> a acp:Policy ; acp:allow acl:Read ;\n"
      "     acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] ."),
     "2 access control resource(s) and 1 target(s)"),
    # Not that an indented block is refused — it is valid Markdown and now valid here. What must
    # fail is its *content*, which is only possible if the block was seen at all: were fences still
    # anchored at column one, this would report a context with no grant instead.
    ("a wrong expectation in a fence indented the three spaces CommonMark allows",
     ("```turtle grant\n[] acp:grant acl:Read .\n```", "   ```turtle grant\n   # nothing\n   ```"),
     "expected {—}, got {acl:Read}"),
    ("a literal where an access mode belongs",
     ("acp:allow acl:Read ;", 'acp:allow "acl:Read" ;'), "and a mode is an IRI"),
    ("a construct the sempods profile excludes",
     ("acp:allow acl:Read ;", "acp:allow acl:Read ; acp:noneOf [ a acp:Matcher ; "
      "acp:agent <https://m.example/#me> ] ;"), "the sempods profile excludes"),
    ("a requirement identifier that validates through its valid prefix",
     ("```turtle acr", "Cites SPS-GRANT-003x.\n\n```turtle acr"),
     "not the shape of a requirement id"),
    ("a context block holding two attempts, which would be composed like a decision",
     ("[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .",
      "[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n"
      "[ acp:target <https://a.example/d> ; acp:agent <https://b.example/#me> ] ."),
     "exactly one node carrying acp:target"),
    ("a reserved individual on an attribute it does not belong to",
     ("acp:agent <https://b.example/#me> ]", "acp:agent acp:PublicClient ]"),
     "not one of the individuals ACP defines for it"),
    ("a mode WAC defines that the sempods profile does not",
     ("acp:allow acl:Read ;", "acp:allow acl:Append ;"), "no permission for"),
    ("a policy stating acl:Write without the acl:Read the profile expands it to",
     ("acp:allow acl:Read ;", "acp:allow acl:Write ;"), "expands when the policy is written"),
    ("anonymous write, which the profile does not permit",
     ("acp:allow acl:Read ;\n     acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .",
      "acp:allow acl:Read, acl:Write ;\n"
      "     acp:anyOf [ a acp:Matcher ; acp:agent acp:PublicAgent ] ."),
     "public matcher for read only"),
    ("a literal where an authorization target belongs",
     ("acp:resource <https://a.example/c> ;", 'acp:resource "https://a.example/c" ;'),
     "and a target is an IRI"),
    ("halves of a decision presenting different credentials",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr\n[ a acp:AccessControlResource ; acp:resource <https://a.example/d> ] .\n```\n"
      "```turtle decision\n"
      "[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ;\n"
      "  acp:vc <https://a.example/vc1> ] .\n"
      "[ acp:target <https://a.example/d> ; acp:agent <https://b.example/#me> ;\n"
      "  acp:vc <https://a.example/vc2> ] .\n```"),
     "present different acp:vc"),
    ("a blank node where an access mode belongs",
     ("acp:allow acl:Read ;", "acp:allow [ ] ;"), "a blank node, and a mode is an IRI"),
    ("a misspelled class on a grant block",
     ("[] acp:grant acl:Read .", "[] a acp:AccessGrannt ; acp:grant acl:Read ."),
     "not acp:AccessGrant"),
    ("a shared policy reached only from an access control nothing links to",
     ("```turtle context", "```turtle policy\n<https://a.example/spare> a acp:Policy ; "
      "acp:allow acl:Read .\n[ a acp:AccessControl ; acp:apply <https://a.example/spare> ] .\n```\n"
      "```turtle context"), "no acr applies"),
    ("two decisions of the same kind on one IRI",
     ("```turtle context", "```turtle acr\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/c> ] .\n```\n```turtle context"),
     "a second unqualified acr claims"),
    ("an inline policy no access control resource applies",
     ("<#p> a acp:Policy ;", "<#spare> a acp:Policy ; acp:allow acl:Read ;\n"
      "     acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n"
      "<#p> a acp:Policy ;"), "nothing applies"),
    ("a fence opened with four backticks, which CommonMark allows",
     ("```turtle grant\n[] acp:grant acl:Read .\n```", "````turtle grant\n# nothing\n````"),
     "expected {—}, got {acl:Read}"),
    ("a misplaced known predicate on an access context",
     ("acp:agent <https://b.example/#me> ] .\n```\n```turtle grant",
      "acp:agent <https://b.example/#me> ; acp:allow acl:Write ] .\n```\n```turtle grant"),
     "which describes no request"),
    ("a misspelled class on an access context",
     ("[ acp:target <https://a.example/c>", "[ a acp:Contexxt ; acp:target <https://a.example/c>"),
     "not acp:Context"),
    ("an extension predicate outside a matcher, where it is inert rather than fail-closed",
     ("<#p> a acp:Policy ;", "<#p> a acp:Policy ; <https://a.example/ns/when> \"always\" ;"),
     "outside a matcher"),
    ("one IRI claimed by a qualified and an unqualified acr",
     ("```turtle context", "```turtle acr-resource\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/c> ] .\n```\n```turtle context"),
     "qualified and an unqualified acr"),
    ("a second node in a context block that no case reads",
     ("[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .",
      "[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n"
      "[ a acp:Context ] ."), "carries no acp:target"),
    ("a literal identity, which SPS-AUTH-049 refuses",
     ("acp:agent <https://b.example/#me> ]", 'acp:agent "bob" ]'),
     "an identity is an IRI"),
    ("a requirement identifier trailing punctuation the token class once stopped at",
     ("```turtle acr", "Cites SPS-GRANT-003_bad.\n\n```turtle acr"),
     "not the shape of a requirement id"),
    ("an untyped policy applied by an access control nothing links to",
     ("```turtle context", "```turtle acr\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/d> ;\n"
      "  acp:accessControl [ acp:apply <#reached> ] ] .\n"
      "<#reached> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n"
      "[ a acp:AccessControl ; acp:apply <#stray> ] .\n"
      "<#stray> acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n```\n"
      "```turtle context"), "nothing applies"),
    ("a half of a larger decision naming an IRI that carries two decisions",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr-context\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/d> ] .\n```\n"
      "```turtle acr-resource\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/d> ] .\n```\n"
      "```turtle decision\n"
      "[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n"
      "[ acp:target <https://a.example/d> ; acp:agent <https://b.example/#me> ] .\n```"),
     "cannot say which of them it means"),
    ("a structural link pointing at a literal",
     ("acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ]", 'acp:anyOf "matcher"'),
     "points at the literal"),
    ("a request predicate inside an authorization graph",
     ("acp:resource <https://a.example/c> ;",
      "acp:resource <https://a.example/c> ; acp:owner <https://o.example/#me> ;"),
     "belongs to a context or grant block"),
    ("a typed matcher no policy references",
     ("<#p> a acp:Policy ;", "<#stray> a acp:Matcher ; acp:agent <https://b.example/#me> .\n"
      "<#p> a acp:Policy ;"), "no policy references"),
    ("a class disagreeing with the role the links give the node",
     ("<#p> a acp:Policy ;", "<#p> a acp:AccessControl ;"), "is typed acp:AccessControl"),
    ("an info string separated from its fence, which CommonMark renders",
     ("```turtle grant\n[] acp:grant acl:Read .\n```", "``` turtle grant\n# nothing\n```"),
     "expected {—}, got {acl:Read}"),
    ("an unapplied inline policy whose IRI another block applies",
     ("```turtle context", "```turtle acr\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/d> ;\n"
      "  acp:accessControl [ acp:apply <https://a.example/shared> ] ] .\n"
      "<https://a.example/shared> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n```\n"
      "```turtle acr\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/e> ] .\n"
      "<https://a.example/shared> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n```\n"
      "```turtle context"), "nothing applies"),
    ("a structural link pointing at a term ACP defines",
     ("acp:apply <#p> ]", "acp:apply acp:Polciy ]"), "ACP's own terms are not"),
    ("a citation whose link ends at a different requirement",
     ("```turtle acr", "See [SPS-GRANT-003](../spec/core/grants.md#SPS-GRANT-009).\n\n```turtle acr"),
     "ends at #SPS-GRANT-009"),
    ("a closing fence longer than its opener, which CommonMark allows",
     ("```turtle grant\n[] acp:grant acl:Read .\n```", "```turtle grant\n# nothing\n````"),
     "expected {—}, got {acl:Read}"),
    ("a closing fence of the other fence character, which does not close the block",
     ("```turtle grant\n[] acp:grant acl:Read .\n```", "```turtle grant\n# nothing\n~~~"),
     "kind that is not one of"),
    ("an ACP term used as an access mode",
     ("acp:allow acl:Read ;", "acp:allow acp:Raed ;"), "ACP defines no access modes"),
    ("a structural link to a node the graph says nothing about",
     ("acp:apply <#p> ]", "acp:apply <#missing> ]"), "says nothing about"),
    ("an access control no access control resource holds",
     ("<#p> a acp:Policy ;", "[ a acp:AccessControl ] .\n<#p> a acp:Policy ;"),
     "no access control resource holds"),
    ("a requirement link that stops at the chapter",
     ("```turtle acr", "See [SPS-GRANT-003](../spec/core/grants.md).\n\n```turtle acr"),
     "the chapter rather than the requirement"),
    ("halves of a decision disagreeing about the pod owner",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr\n[ a acp:AccessControlResource ; acp:resource <https://a.example/d> ] .\n```\n"
      "```turtle decision\n"
      "[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ;\n"
      "  acp:owner <https://o.example/#me> ] .\n"
      "[ acp:target <https://a.example/d> ; acp:agent <https://b.example/#me> ;\n"
      "  acp:owner <https://b.example/#me> ] .\n```"),
     "disagree about acp:owner"),
    ("a foreign class on a node no link reaches",
     ("<#p> a acp:Policy ;", "[ a <https://a.example/ns/Condition> ] .\n<#p> a acp:Policy ;"),
     "types a node no link reaches"),
    ("two owners in a standalone context case",
     ("acp:agent <https://b.example/#me> ] .\n```\n```turtle grant",
      "acp:agent <https://b.example/#me> ;\n  acp:owner <https://o.example/#me>, "
      "<https://p.example/#me> ] .\n```\n```turtle grant"),
     "and a pod records one"),
    ("a fixture fence inside a block quote, which renders and never runs",
     ("```turtle grant\n[] acp:grant acl:Read .\n```",
      "> ```turtle grant\n> [] acp:grant acl:Read .\n> ```"),
     "inside a block quote or a nested list"),
    ("a reference-style citation resolving to a different requirement",
     ("```turtle acr", "See [SPS-GRANT-003][wrong].\n\n[wrong]: ../spec/core/grants.md#SPS-GRANT-009\n\n```turtle acr"),
     "ends at #SPS-GRANT-009"),
    ("an access control resource smuggled into a policy block",
     ("```turtle context", "```turtle policy\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/d> ;\n"
      "  acp:accessControl [ acp:apply <https://a.example/q> ] ] .\n"
      "<https://a.example/q> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n```\n"
      "```turtle context"), "a shared artifact is a policy and its matchers"),
    ("a fixture fence opened inside a list item",
     ("```turtle grant\n[] acp:grant acl:Read .\n```",
      "- ```turtle grant\n  [] acp:grant acl:Read .\n  ```"),
     "inside a block quote or a nested list"),
    ("a shortcut reference resolving to a different requirement",
     ("```turtle acr",
      "See [SPS-GRANT-003].\n\n[SPS-GRANT-003]: ../spec/core/grants.md#SPS-GRANT-009\n\n```turtle acr"),
     "ends at #SPS-GRANT-009"),
    ("a class assertion smuggled into a policy block",
     ("```turtle context", "```turtle policy\n[ a acp:AccessControlResource ] .\n```\n```turtle context"),
     "a shared artifact is a policy and its matchers"),
    ("a reference definition whose label differs only in case",
     ("```turtle acr",
      "See [SPS-GRANT-003].\n\n[sps-grant-003]: ../spec/core/grants.md#SPS-GRANT-009\n\n```turtle acr"),
     "ends at #SPS-GRANT-009"),
    ("anonymous write through the public *client*",
     ("acp:allow acl:Read ;\n     acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .",
      "acp:allow acl:Read, acl:Write ;\n"
      "     acp:anyOf [ a acp:Matcher ; acp:client acp:PublicClient ] ."),
     "public matcher for read only"),
    ("an acr block adding triples to a shared policy",
     ("```turtle context", "```turtle policy\n<https://a.example/shared> a acp:Policy ;\n"
      "  acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n```\n"
      "```turtle acr\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/d> ;\n"
      "  acp:accessControl [ acp:apply <https://a.example/shared> ] ] .\n"
      "<https://a.example/shared> acp:allow acl:Write .\n```\n"
      "```turtle context"), "a shared artifact has one version"),
    ("acl:Control outside a resource decision",
     ("```turtle acr\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/c> ;\n"
      "  acp:accessControl [ acp:apply <#p> ] ] .\n"
      "<#p> a acp:Policy ; acp:allow acl:Read ;",
      "```turtle acr-context\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/c> ;\n"
      "  acp:accessControl [ acp:apply <#p> ] ] .\n"
      "<#p> a acp:Policy ; acp:allow acl:Read, acl:Write, acl:Control ;"),
     "outside an acr-resource or acr-delegation block"),
    ("a fixture inside an HTML comment, which no reader sees",
     ("```turtle grant\n[] acp:grant acl:Read .\n```",
      "```turtle grant\n[] acp:grant acl:Read .\n```\n<!--\n```turtle grant\n# nothing\n```\n-->"),
     "inside an HTML comment"),
    ("a fixture inside a raw HTML block, which renders as backticks",
     ("```turtle grant\n[] acp:grant acl:Read .\n```",
      "```turtle grant\n[] acp:grant acl:Read .\n```\n<pre>\n```turtle grant\n# nothing\n```\n</pre>"),
     "inside a raw HTML block"),
    ("an access control smuggled into a policy block",
     ("```turtle context", "```turtle policy\n[ a acp:AccessControl ; acp:apply "
      "<https://a.example/q> ] .\n<https://a.example/q> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n```\n"
      "```turtle context"), "a shared artifact is a policy and its matchers"),
    ("a ceiling composed with a target anyone can read",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/open> ;\n"
      "  acp:accessControl [ acp:apply <#pub> ] ] .\n"
      "<#pub> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent acp:PublicAgent ] .\n```\n"
      "```turtle acr-delegation\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://b.example/#me> ;\n"
      "  acp:accessControl [ acp:apply <#ceil> ] ] .\n"
      "<#ceil> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:client <did:web:app.example> ] .\n```\n"
      "```turtle decision\n"
      "[ acp:target <https://a.example/open> ; acp:agent <https://b.example/#me> ] .\n"
      "[ acp:target <https://b.example/#me> ; acp:agent <https://b.example/#me> ] .\n```"),
     "the public branch unions where this block intersects"),
    ("a composed decision with no context half",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr-resource\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/d> ] .\n```\n"
      "```turtle decision\n"
      "[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n"
      "[ acp:target <https://a.example/d> ; acp:agent <https://b.example/#me> ] .\n```"),
     "composes no context decision"),
    ("a delegation half naming somebody other than the requester",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr-context\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://a.example/ctx> ] .\n```\n"
      "```turtle acr-delegation\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://alice.example/#me> ] .\n```\n"
      "```turtle decision\n"
      "[ acp:target <https://a.example/ctx> ; acp:agent <https://b.example/#me> ] .\n"
      "[ acp:target <https://alice.example/#me> ; acp:agent <https://b.example/#me> ] .\n```"),
     "a ceiling bounds the principal it names"),
    ("a literal where a class assertion belongs",
     ("<#p> a acp:Policy ;", '<#p> a "Policy" ;'), "not a class"),
    ("a requirement id with a word character stuck to its front",
     ("```turtle acr", "See XSPS-GRANT-003.\n\n```turtle acr"),
     "not the shape of a requirement id"),
    ("a repeated reference label whose first definition is the wrong one",
     ("```turtle acr", "See [SPS-GRANT-003].\n\n[SPS-GRANT-003]: ../spec/core/grants.md#SPS-GRANT-009\n"
      "[SPS-GRANT-003]: ../spec/core/grants.md#SPS-GRANT-003\n\n```turtle acr"),
     "ends at #SPS-GRANT-009"),
    # Two the checker used to get wrong itself: it crashed on the first and rejected the second.
    ("an acr block typed but carrying no target",
     ("```turtle acr", "```turtle acr\n[ a acp:AccessControlResource ] .\n```\n```turtle acr"),
     "0 target(s)"),
    # `<!DOCTYPE html>` would close on its own line, so the declaration is left open on purpose.
    ("a fixture inside a CommonMark declaration block",
     ("```turtle grant\n[] acp:grant acl:Read .\n```",
      "```turtle grant\n[] acp:grant acl:Read .\n```\n<!DOCTYPE\n"
      "```turtle grant\n# nothing\n```\nhtml>"),
     "inside a raw HTML block"),
    ("a fixture inside a custom element, which CommonMark treats as raw HTML",
     ("```turtle grant\n[] acp:grant acl:Read .\n```",
      "```turtle grant\n[] acp:grant acl:Read .\n```\n<my-widget>\n"
      "```turtle grant\n# nothing\n```"),
     "inside a raw HTML block"),
    ("acp:attribute, the super-property, used as an attribute",
     ("acp:agent <https://b.example/#me> ]", "acp:attribute <https://b.example/#me> ]"),
     "the super-property rather than an attribute"),
    ("a grant block node that carries no acp:grant",
     ("[] acp:grant acl:Read .", "[] acp:grant acl:Read .\n[ a acp:AccessGrant ] ."),
     "carries no acp:grant, so it says nothing"),
    ("a ceiling naming no client, so every application acting as the person has it",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr-delegation\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://b.example/#me> ;\n"
      "  acp:accessControl [ acp:apply <#ceil> ] ] .\n"
      "<#ceil> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] .\n```\n"
      "```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```"),
     "grants without naming an application"),
    ("a ceiling open to every authenticated application",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr-delegation\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://b.example/#me> ;\n"
      "  acp:accessControl [ acp:apply <#ceil> ] ] .\n"
      "<#ceil> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:allOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] ,\n"
      "            [ a acp:Matcher ; acp:client acp:AuthenticatedClient ] .\n```\n"
      "```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```"),
     "grants without naming an application"),
    ("a reference definition whose label carries surrounding space",
     ("```turtle acr",
      "See [SPS-GRANT-003].\n\n[ SPS-GRANT-003 ]: ../spec/core/grants.md#SPS-GRANT-009\n\n```turtle acr"),
     "ends at #SPS-GRANT-009"),
    ("a ceiling whose alternatives do not all name an application",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr-delegation\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://b.example/#me> ;\n"
      "  acp:accessControl [ acp:apply <#ceil> ] ] .\n"
      "<#ceil> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ;\n"
      "              acp:issuer <https://issuer.example> ] ,\n"
      "            [ a acp:Matcher ; acp:client <did:web:app.example> ] .\n```\n"
      "```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```"),
     "grants without naming an application"),
    ("a reference definition inside a code fence, which renders as text",
     ("```turtle acr",
      "See [SPS-GRANT-003].\n\n```text\n[SPS-GRANT-003]: ../spec/core/grants.md#SPS-GRANT-003\n```\n\n"
      "[SPS-GRANT-003]: ../spec/core/grants.md#SPS-GRANT-009\n\n```turtle acr"),
     "ends at #SPS-GRANT-009"),
    ("a ceiling naming an application and every authenticated one beside it",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```",
      "```turtle acr-delegation\n[ a acp:AccessControlResource ;\n"
      "  acp:resource <https://b.example/#me> ;\n"
      "  acp:accessControl [ acp:apply <#ceil> ] ] .\n"
      "<#ceil> a acp:Policy ; acp:allow acl:Read ;\n"
      "  acp:allOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ] ,\n"
      "            [ a acp:Matcher ; acp:client <did:web:app.example>, acp:AuthenticatedClient ] .\n```\n"
      "```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```"),
     "grants without naming an application"),
    ("a reference definition whose destination is on the next line",
     ("```turtle acr",
      "See [SPS-GRANT-003].\n\n[SPS-GRANT-003]:\n  ../spec/core/grants.md#SPS-GRANT-009\n\n```turtle acr"),
     "ends at #SPS-GRANT-009"),
    ("a fixture inside a custom element opened after a heading",
     ("```turtle grant\n[] acp:grant acl:Read .\n```",
      "```turtle grant\n[] acp:grant acl:Read .\n```\n\n## Heading\n<my-widget>\n"
      "```turtle grant\n# nothing\n```"),
     "inside a raw HTML block"),
    ("a decision composed by union rather than intersection",
     ("```turtle context\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n```\n"
      "```turtle grant\n[] acp:grant acl:Read .\n```",
      "```turtle acr\n[ a acp:AccessControlResource ; acp:resource <https://a.example/d> ] .\n```\n"
      "```turtle decision\n[ acp:target <https://a.example/c> ; acp:agent <https://b.example/#me> ] .\n"
      "[ acp:target <https://a.example/d> ; acp:agent <https://b.example/#me> ] .\n```\n"
      "```turtle grant\n[] acp:grant acl:Read .\n```"),
     "expected {acl:Read}"),
    ("a matcher mixing an extension with an ACP attribute, which widens the answer",
     ("acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ]",
      "acp:anyOf [ a acp:Matcher ; acp:agent <https://b.example/#me> ;\n"
      "                            <https://a.example/ns/set> <https://a.example/g> ]"),
     "two acp:allOf matchers"),
    ("a request claiming to be a reserved individual, which §6.5.2 would let through",
     ("acp:target <https://a.example/c> ; acp:agent <https://b.example/#me>",
      "acp:target <https://a.example/c> ; acp:agent acp:OwnerAgent"), "describes no request"),
]


def self_test(ids: set[str]) -> int:
    import tempfile

    problems: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "fixture.md"

        def failures_of(text: str) -> list[str]:
            path.write_text(text, encoding="utf-8")
            return check_scenario(path, ids)[0]

        if failures_of(SOUND):
            problems.append("the sound fixture does not pass, so no rejection below proves anything")
        for description, (before, after), wording in BROKEN:
            assert before in SOUND, f"self-test fixture no longer contains {before!r}"
            # One occurrence. Replacing every one lets a second guard report the same wording and
            # keep this case green after the guard it is for has regressed.
            reported = failures_of(SOUND.replace(before, after, 1))
            if not any(wording in failure for failure in reported):
                problems.append(f"{description}: not rejected, or not named as {wording!r}")

    for problem in problems:
        print(f"FAIL self-test: {problem}")
    if problems:
        return 1
    print(f"{len(BROKEN)} way(s) of being wrong are still caught.")
    return 0


def main(argv: list[str]) -> int:
    if not INDEX.exists():
        print(f"{INDEX} is missing; run check-requirements.py --write-index first", file=sys.stderr)
        return 1
    ids = {r["id"] for r in json.loads(INDEX.read_text(encoding="utf-8"))["requirements"]}

    if argv == ["--self-test"]:
        return self_test(ids)

    paths = [Path(a).resolve() for a in argv] or sorted(EXAMPLES.rglob("*.md"))
    paths = [p for p in paths if p != EXAMPLES / "README.md"]
    if not paths:
        # A passing loop over nothing would let the required check stay green while the promised
        # coverage had been deleted — the same trap the OpenAPI job guards against.
        print("no scenarios found: examples/ holds nothing to check", file=sys.stderr)
        return 1

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
