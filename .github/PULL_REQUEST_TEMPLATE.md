<!-- Keep this short. What the change does and why it is right are the parts a reviewer
     cannot read off the diff; everything else is already in the diff. -->

## What this changes

<!-- One or two sentences. Link the issue if there is one: "Closes #123". -->

## Why

<!-- A specification change needs a written rationale, because other implementations
     depend on it. If an implementation already runs this, say so — running code carries
     more weight here than a good argument. -->

## Before requesting review

- [ ] Every commit is signed off — `git commit -s`, or `dco` fails
- [ ] Every new normative statement has a requirement ID, and its anchor matches it
      exactly
- [ ] **No requirement ID was reused, renumbered or deleted.** A requirement that is no
      longer wanted is marked *withdrawn* and keeps its ID — it is cited in conformance
      suites and in other people's test reports
- [ ] The OpenAPI description moved with the chapter, if the HTTP surface moved
- [ ] `spec/README.md`'s chapter table still reflects reality
- [ ] The roadmap item is ticked, in this same change
- [ ] `lychee --offline --include-fragments --no-progress --exclude-path site .` passes

<!-- Is this a breaking change to the contract? Say so here. The project is 0.x and
     breaking is allowed — it is just never meant to be accidental or silent. -->
