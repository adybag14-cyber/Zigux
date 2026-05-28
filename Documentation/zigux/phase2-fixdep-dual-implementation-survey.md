# Phase 2 fixdep dual-implementation survey

Lane: `P2-L01`

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records a bounded fixdep lane around `scripts/zigux/fixdep.zig` together with the dedicated parity checker, fixture packet, and wrapper-backed follow-through, so this family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` still directly serves `scripts/zigux/fixdep.zig`, so the core Zig-side dual-implementation helper remains present on head.
- Current `master` also directly serves `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/validate-phase2.py`, so the helper, dedicated gate, parity checker, and shared Phase 2 validator packet are all materialized together.
- Current `master` directly serves `zigux/tests/fixtures/fixdep/cases.json`, which now carries the bounded thirteen-case external fixdep packet, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_double_backslash_comment`, and the current `/dev/full` stdout-failure replays.
- The live `zigux/Makefile` still exposes `phase2-fixdep` with the dedicated fixdep gate self-test, fixdep gate run, fixdep diff self-test, fixdep diff run, and `zig test scripts/zigux/fixdep.zig` replay.
- The live `.github/workflows/zigux-bootstrap.yml` still replays the same fixdep packet on current `master` through the dedicated gate self-test and run, the fixdep diff self-test and run, `make -C zigux phase2-fixdep`, and the direct `zig test scripts/zigux/fixdep.zig` step.
- The shared reminder packet in `Documentation/zigux/phase2-closure.md` and `zigux/tests/README.md` now also treats the fixdep helper, parity checker, fixture roster, and wrapper route as current repo evidence.
- Those same shared reminder surfaces still do not enumerate `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md` alongside the genksyms survey, so the fixdep dual-implementation survey itself remains outside the shared Phase 2 reminder packet.
- Current `master` now directly serves `Documentation/zigux/artifact-diff.md`, so the older reminder-side companion gap recorded in this survey is no longer live.
- Current `scripts/zigux/fixdep.zig` already captures `error.PermissionDenied` on the dedicated `fixdep: error opening file:` path, and the live helper also carries a focused regression test for that branch.
- Exact-path authenticated contents reads still return missing for `scripts/basic/fixdep.c`, so the roadmap's C-side anchor remains unreadable through the primary repo-read path used for this survey refresh.

## Survey result

- The roadmap-backed Zigux-side fixdep packet is currently present on `master`.
- The live repo no longer supports the older survey claim that the fixdep fixture packet stops at twelve external cases. The bounded fixdep packet is now thirteen cases wide and already includes the later dependency-continuation, comment-continuation, and double-backslash-comment parity paths.
- The live repo also no longer supports the older survey claim that `Documentation/zigux/artifact-diff.md` is missing: current authenticated contents readback now returns that reminder-side companion directly on `master`.
- The live repo no longer supports the older survey claim that the helper still omits `error.PermissionDenied` from the dedicated open-file capture set. Current `scripts/zigux/fixdep.zig` already captures that branch and ships a focused regression test for it.
- The honest remaining repo-versus-roadmap gap is now narrower: the roadmap C-side anchor `scripts/basic/fixdep.c` still remains unreadable through authenticated exact-path contents reads in this runtime, and the shared Phase 2 closure and tests-root reminders still do not enumerate this fixdep survey even though they already enumerate the genksyms survey.
- The honest lane result is therefore a survey-truthfulness refresh plus lane-local gate follow-through, not a new fixdep behavior, fixture, or route implementation. The shared reminder follow-through for the missing survey pointer still belongs to the shared Phase 2 reminder lane rather than this survey lane.

## Next bounded same-family step

The current repo evidence now supports one fixdep-only next-safe-step note: make a one-file closure correction in `Documentation/zigux/phase2-closure.md` so the shared Phase 2 closure packet enumerates `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, then stop and leave the broader tests-root reminder follow-through to the shared Phase 2 reminder lane.

1. Use `P2-Y02` only for that one-file closure correction in `Documentation/zigux/phase2-closure.md`.
2. Leave `zigux/tests/README.md` out of this lane unless the shared Phase 2 reminder lane explicitly reopens it.
3. If a future current-head reread makes `scripts/basic/fixdep.c` directly readable through the authenticated exact-path contents route again, refresh this survey note to retire the degraded-read gap.
4. If a future fixdep behavior lane widens the helper-local regression packet again, keep the gate and survey aligned in the same run so the survey does not fall behind landed code.
5. Do not widen from this survey into genksyms, kconfig, parser behavior, or shared Phase 2 reminder maintenance.
