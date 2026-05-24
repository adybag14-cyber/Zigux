# Phase 2 fixdep next step note

Lane: `P2-L06`

Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor, and the live fixdep governance packet remains broader and healthier than older reminder wording suggested.

## Roadmap and ledger grounding

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records the bounded fixdep tranche around `scripts/zigux/fixdep.zig` together with parity-companion and workflow-backed follow-through, so the family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/fixdep.zig`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/validate-phase2.py`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, `Documentation/zigux/phase2-fixdep-next-step-note.md`, `Documentation/zigux/artifact-diff.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zigux/tests/README.md`, and `zigux/tests/fixtures/fixdep/cases.json`.
- `zigux/tests/fixtures/fixdep/cases.json` currently inventories 13 external fixdep cases, including `sample_dependency_continuation`, `sample_comment_continuation`, and the widened `sample_multi_target_stdout_full` replay beside the current stdout-failure packet.
- The live bootstrap workflow and `zigux/Makefile` still expose direct fixdep replay routes through `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py`, `make -C zigux phase2-fixdep`, and `zig test scripts/zigux/fixdep.zig`.
- The shared closure note and tests-root reminder both keep the fixdep helper, checker pair, fixture roster, and wrapper route explicit as current repo evidence.
- Repeated exact-path contents reads still return missing for `scripts/basic/fixdep.c`, but the live parity packet now stays bounded to `scripts/zigux/fixdep.zig`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and the committed fixture packet while `Documentation/zigux/artifact-diff.md` keeps the shared comparison helper explicit.

## Survey result

- The older same-lane reminder drift around supposedly missing fixdep governance, wrapper, and fixture coverage is now closed by current repo evidence.
- The current diff-and-fixture packet is truthful again: `scripts/zigux/check-fixdep-diff.py` now validates the Zig helper path, the thirteen-case fixture roster, the committed expected-output files, and deterministic repeat runs without depending on a readable `scripts/basic/fixdep.c` path.
- Widening this lane into parser behavior, expected-output growth, or shared Phase 2 reminder maintenance would skip over the honest current result, which is to keep the lane parked until a fresh fixdep-local failure appears.

## Next safe step

1. Keep `P2-L06` parked unless a fresh current-`master` reread finds new drift inside the live fixdep helper, checker, fixture, or route packet.
2. If the fixdep family reopens, start with one smallest same-family follow-through only: either close a new direct mismatch in `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, or `zigux/tests/fixtures/fixdep/cases.json`, or restore a fresh live parity anchor only if the checker grows to require it again.
3. Do not widen from this reminder lane into parser behavior, fixture expected outputs, genksyms, kconfig bridge, or the broader shared Phase 2 route inventory without a new direct fixdep failure signal.
