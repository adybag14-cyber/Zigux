# Zigux Pull Request Checklist

Use this template for bounded product work in `adybag14-cyber/Zigux`.

## Scope
- roadmap phase:
- lane or workstream:
- Linux anchor file or tree path:
- bounded non-goals:

## What Changed
- summarize the user-facing or reviewer-facing change in a few lines
- name the exact helper, validator, survey packet, or documentation surface touched

## Validation
- validator-first command run:
- focused Zig replay or shared build replay run:
- checker self-tests or fixture checks run:
- if a local replay was not possible, explain the exact blocker:

## Docs And Workflow Sync
- if this PR touches validator scripts, shared build entrypoints, workflow steps, inventories, or review packets, confirm whether these were updated in the same change when applicable:
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - the relevant `Documentation/zigux/*.md` note, survey, or checklist
- name any exact checker, survey packet, or manifest added or changed:
- note whether the change affects a shared replay path, a dedicated replay path, or both:

## Safety
- rollback owner and fallback path:
- freeze-map, ABI, unsafe, or runtime-boundary impact:
- active blocker or follow-up left open:

## Reviewer Notes
- validator-first delivery is the default in Zigux: document the exact command reviewers should rerun first
- if a new checker or survey packet was added, keep the contributor-facing guidance aligned in the same PR instead of leaving the route discoverable only from code or workflow wiring
- if the work is documentation-only because the repo checkout or toolchain was unavailable, say that plainly and name the exact repo state inspected
