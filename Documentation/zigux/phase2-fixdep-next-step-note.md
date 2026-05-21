# Phase 2 fixdep next step note

Lane: `P2-L06`

Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor, and the live fixdep governance packet remains broader and healthier than older reminder wording suggested.

## Roadmap and ledger grounding

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records the bounded fixdep tranche around `scripts/zigux/fixdep.zig` together with parity-companion and workflow-backed follow-through, so the family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/fixdep.zig`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/validate-phase2.py`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, `Documentation/zigux/phase2-fixdep-next-step-note.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/fixtures/fixdep/cases.json`.
- `zigux/tests/fixtures/fixdep/cases.json` currently inventories 13 external fixdep cases, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_double_backslash_comment`, and the current stdout-failure replay cases.
- The live bootstrap workflow and `zigux/Makefile` still expose direct fixdep replay routes through `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig`.
- The current bounded drift is narrower: direct current-`master` readback for `scripts/basic/fixdep.c` still returns missing through the same contents path, while `scripts/zigux/check-fixdep-diff.py` still hard-codes that file as both `C_FIXDEP` and `EXPECTED_C_FIXDEP`, so the diff checker no longer points at a fully readable in-repo C anchor.

## Survey result

- The same-lane gap is now checker-anchor truthfulness, not missing fixdep artifact support and not helper-local parser drift.
- The fixdep helper, checker pair, fixture roster, and direct replay routes remain reviewable on current `master`.
- Widening this lane into parser or new expected-output work would skip over the smaller governance correction still needed around the diff checker's readable C reference.

## Next safe step

1. Keep `P2-L06` parked unless a fresh current-`master` reread finds a new reminder mismatch inside the fixdep closure packet.
2. If the fixdep family reopens, keep the follow-through to one same-family checker or reminder correction only: either restore a readable current-`master` C anchor at `scripts/basic/fixdep.c` or narrow `scripts/zigux/check-fixdep-diff.py` to a truthful available reference path or documented fallback.
3. Do not widen from this governance lane into parser behavior, fixture expected outputs, genksyms, kconfig bridge, or the broader shared Phase 2 route inventory.
