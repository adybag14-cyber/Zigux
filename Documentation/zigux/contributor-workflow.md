# Zigux Contributor Workflow

This guide keeps routine Zigux product work small, reviewable, and tied to current repo evidence.

Use it with `CONTRIBUTING.md`, `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`, `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/contributor-entrypoints.md`, `Documentation/zigux/developer-enablement-contributor-workflow.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.

## 1. Start With The Current Tree

- inspect the current `master` state before choosing work
- compare what is live in the repo with the roadmap, the ledger, and the nearest shared reminder surfaces
- prefer one bounded gap that is still unfinished on current `master`

## 2. Stay Inside One Lane

- name the lane, phase, and target family up front
- keep the write set inside that lane unless current repo reality blocks the exact target
- do not turn reminder work into wrapper churn, mirror-tree sprawl, or broad phase switching

## 3. Pick Work That Counts

Good developer-enablement work includes:

- docs that clarify current product boundaries or active review surfaces
- checklists that keep reminder packets honest across docs, scripts, tests, manifests, and wrappers
- contributor workflow notes that reduce repeat confusion about validation, ownership, or publication
- small guard updates that verify a shared reminder surface still matches current `master`

Avoid treating these as meaningful progress by themselves:

- duplicative reminder files that do not close a real gap
- restating roadmap text without tying it to live repo evidence
- adding new wrapper names or route claims that current `master` does not actually ship

## 4. Tie The Change To Reviewable Evidence

- name the owning phase, the direct anchors, and the exact validation surface you are updating
- keep reminder prose aligned with the validator, manifest, build route, and current packet members that actually exist
- if a path is missing on current `master`, frame it as historical, parked, or blocked evidence instead of current proof

## 5. Validate In Validator-First Order

- for docs-only work, verify the touched file names, route names, and status buckets against current repo reads
- for checklist or guard changes, run the narrowest self-test or focused validator before broader wrapper routes when both exist
- for top-level contributor onboarding changes, rerun `python3 scripts/zigux/check-contributor-onboarding-packet.py` so `CONTRIBUTING.md`, `Documentation/zigux/contributor-entrypoints.md`, and this workflow note stay aligned
- for docs-only reminder, checklist, or contributor workflow guidance changes, rerun `python3 scripts/zigux/check-developer-enablement-workflow.py` so `Documentation/zigux/contributor-entrypoints.md`, `Documentation/zigux/developer-enablement-contributor-workflow.md`, and this workflow note keep the same docs-only handoff
- for Zig or mixed-source changes, prefer the smallest relevant `zig build ...`, `make -C zigux ...`, or checker replay before claiming success
- if the full replay path is unavailable, record the degraded path and the exact boundary it leaves unproven

## 6. Publish And Close The Loop

- keep the change focused enough to explain in one short summary
- report what changed, what was validated, what stayed out of scope, and what the next bounded step should be
- use the GitHub app publication path when landing validated work onto `master`
- if publication is blocked, keep the exact patch intact and record the blocker plus the next bounded step

## Quick Entry Points

- `CONTRIBUTING.md`: top-level contributor starting map and bounded onboarding reminders
- `Documentation/zigux/README.md`: docs-root packet inventory and phase reminders
- `Documentation/zigux/contributor-entrypoints.md`: bounded guide selection for docs, checklist, and workflow work
- `Documentation/zigux/developer-enablement-contributor-workflow.md`: docs-only reminder, checklist, and contributor workflow guidance handoff
- `Documentation/zigux/review-checklist.md`: pre-merge review prompts and phase safety checks
- `scripts/zigux/README.md`: validator-first and checker-first reminder routes
- `zigux/tests/README.md`: tests-root replay packets and focused build surfaces