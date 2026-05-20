# Phase 2 fixdep dual-implementation survey

Lane: `P2-L01`

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records a bounded fixdep lane around `scripts/zigux/fixdep.zig` together with the dedicated parity checker, fixture packet, and wrapper-backed follow-through, so this family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` still directly serves `scripts/zigux/fixdep.zig`, so the core dual-implementation helper remains present on head.
- Current `master` also directly serves `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/validate-phase2.py`, so the helper, dedicated gate, parity checker, and shared Phase 2 validator packet are all materialized together.
- Current `master` directly serves `zigux/tests/fixtures/fixdep/cases.json`, which now carries the bounded twelve-case external fixdep packet including `sample_dependency_continuation`.
- The live `zigux/Makefile` still exposes `phase2-fixdep` with the dedicated fixdep gate self-test, fixdep gate run, fixdep diff self-test, fixdep diff run, and `zig test scripts/zigux/fixdep.zig` replay.
- The live `.github/workflows/zigux-bootstrap.yml` still replays the same fixdep packet on current `master` through the dedicated gate self-test and run, the fixdep diff self-test and run, and the direct `zig test scripts/zigux/fixdep.zig` step.
- The shared reminder packet in `Documentation/zigux/phase2-closure.md` and `zigux/tests/README.md` now also treats the fixdep helper, parity checker, fixture roster, and wrapper route as current repo evidence.
- Repeated direct readback still returns missing for `Documentation/zigux/artifact-diff.md`, so one older fixdep-adjacent reminder document remains absent even though the dedicated helper, checker, fixture, and route packet has returned on current `master`.

## Survey result

- The roadmap-backed dual-implementation gap for `scripts/zigux/fixdep.zig` is currently closed on `master`.
- The live repo no longer supports the older survey claim that the fixdep diff checker, fixture roster, or dedicated Makefile and workflow routes are missing.
- The only visible same-family repo-reality gap from this survey pass is the absent `Documentation/zigux/artifact-diff.md` companion, which is now a reminder-surface detail rather than evidence that the dual-implementation packet itself is missing.
- The honest lane result is therefore a survey-note correction and parking pass, not a new fixdep behavior, fixture, or route implementation.

## Next bounded same-family step

1. Keep `P2-L01` parked unless a fresh current-`master` reread finds new repo-versus-roadmap drift inside the fixdep helper, checker, fixture, or route packet.
2. If the fixdep family reopens, keep the follow-through on a directly coupled non-survey lane: either restore `Documentation/zigux/artifact-diff.md` as the remaining reminder-surface companion or fix a newly observed drift in `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, or `Documentation/zigux/phase2-closure.md`.
3. Do not widen from this survey into genksyms, kconfig, parser behavior, or shared Phase 2 reminder maintenance.
