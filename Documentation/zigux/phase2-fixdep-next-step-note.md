# Phase 2 fixdep next step note

Lane: `P2-L06`

Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor, and the live fixdep governance packet remains broader and healthier than older reminder wording suggested.

## Roadmap and ledger grounding

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records the bounded fixdep tranche around `scripts/zigux/fixdep.zig` together with parity-companion and workflow-backed follow-through, so the family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/fixdep.zig`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/validate-phase2.py`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, `Documentation/zigux/phase2-fixdep-next-step-note.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/fixtures/fixdep/cases.json`.
- `scripts/basic/fixdep.c` remains reviewable on current `master` through the public raw GitHub fallback even though the same contents-API read path used by some scheduled rereads still returns that file as missing.
- `zigux/tests/fixtures/fixdep/cases.json` currently inventories 13 external fixdep cases, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_double_backslash_comment`, and the current stdout-failure replay cases.
- The live bootstrap workflow and `zigux/Makefile` still expose direct fixdep replay routes through `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig`.

## Survey result

- The older same-lane reminder drift around a supposedly unreadable in-repo C anchor is now closed by current repo evidence: the direct contents read path still misses `scripts/basic/fixdep.c`, but current `master` does keep the authoritative C fixdep source reachable through raw GitHub fallback.
- The fixdep helper, checker pair, external fixture roster, C anchor, and direct replay routes remain reviewable on current `master`.
- Widening this lane into parser or new expected-output work would skip over the more honest result that the earlier checker-anchor reminder gap is no longer present.

## Next safe step

1. Keep `P2-L06` parked unless a fresh current-`master` reread finds a real checker, fixture, or route mismatch inside the live fixdep packet.
2. If the fixdep family reopens, start with one smallest same-family follow-through that is proven by current repo evidence or a writable-checkout replay, such as a direct checker failure, fixture inventory mismatch, or route drift.
3. Do not widen from this reminder lane into parser behavior, fixture expected outputs, genksyms, kconfig bridge, or the broader shared Phase 2 route inventory without a new same-family failure signal.
