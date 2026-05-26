# Zigux Contributor Workflow

This guide keeps routine Zigux product work small, reviewable, and tied to the roadmap.

## 1. Start With The Current Tree

- inspect the current `master` state before choosing work
- compare what is live in the repo with:
  - `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
  - `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
  - the relevant reminder surfaces under `Documentation/zigux/`, `scripts/zigux/`, and `zigux/tests/`
- prefer one bounded gap that is still unfinished on current `master`

## 2. Stay Inside One Lane

- name the lane, phase, and target family up front
- keep the write set inside that lane unless current repo reality blocks the exact target
- do not turn reminder work into wrapper churn, mirror-tree sprawl, or broad phase switching

## 3. Pick Work That Counts

Good developer-enablement work includes:

- docs that clarify current product boundaries or active review surfaces
- checklists that keep reminder packets honest across docs, scripts, tests, and wrappers
- contributor workflow notes that reduce repeat confusion about validation, ownership, or publication
- small guard scripts that verify a shared reminder surface still matches current `master`

Avoid treating these as meaningful progress by themselves:

- duplicative reminder files that do not close a real gap
- restating roadmap text without tying it to live repo evidence
- adding new wrapper names or route claims that current `master` does not actually ship

## 4. Keep Reminder Surfaces Honest

- if a docs or checklist file summarizes shipped routes, fixtures, or helper families, verify those paths are still present on current `master`
- when current `master` is missing an older path, frame it as historical or parked evidence instead of current proof
- when a route has returned on current `master`, update reminder wording so contributors can rely on it again
- route freeze-map or study-only summaries back through their owner notes instead of treating them as direct delivery proof

## 5. Validate At The Smallest Honest Scope

- for docs-only work, verify the touched file names, route names, and ownership claims against current repo reads
- for checklist or guard changes, run the narrowest available self-test or focused validator
- for Zig or mixed-source changes, prefer the smallest relevant `zig build ...`, `make -C zigux ...`, or checker replay before claiming success
- if the full build is unavailable, state exactly what was validated and what remains unverified

## 6. Publish In A Reviewable Shape

- keep the change focused enough to explain in one short summary
- record the validation that was actually run
- use the GitHub app publication path when landing validated work onto `master`
- if publication is blocked, keep the exact patch intact and record the blocker plus the next bounded step

## 7. Close The Loop

Before finishing a run:

- update the relevant reminder surface or checklist only as far as the validated evidence supports
- record the substantive result, risks, and next bounded step in the shared progress notes
- keep the next recommendation inside the same lane or adjacent roadmap packet unless the lane is truly complete
