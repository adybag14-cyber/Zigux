# Phase 2 fixdep dual-implementation survey

Lane: `P2-L01`

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records a bounded fixdep lane around `scripts/zigux/fixdep.zig` together with the dedicated parity checker, fixture packet, and wrapper-backed follow-through, so this family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` still directly serves `scripts/zigux/fixdep.zig`, so the core dual-implementation helper remains present on head.
- Current `master` also directly serves `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/validate-phase2.py`, so the helper, dedicated gate, parity checker, and shared Phase 2 validator packet are all materialized together.
- Current `master` directly serves `zigux/tests/fixtures/fixdep/cases.json`, which now carries the bounded thirteen-case external fixdep packet, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_double_backslash_comment`, and the current `/dev/full` stdout-failure replays.
- The live `zigux/Makefile` still exposes `phase2-fixdep` with the dedicated fixdep gate self-test, fixdep gate run, fixdep diff self-test, fixdep diff run, and `zig test scripts/zigux/fixdep.zig` replay.
- The live `.github/workflows/zigux-bootstrap.yml` still replays the same fixdep packet on current `master` through the dedicated gate self-test and run, the fixdep diff self-test and run, `make -C zigux phase2-fixdep`, and the direct `zig test scripts/zigux/fixdep.zig` step.
- The shared reminder packet in `Documentation/zigux/phase2-closure.md` and `zigux/tests/README.md` now also treats the fixdep helper, parity checker, fixture roster, and wrapper route as current repo evidence.
- Repeated exact-path contents reads still return missing for both `scripts/basic/fixdep.c` and `Documentation/zigux/artifact-diff.md`, so the remaining same-family gaps are now narrower than the dual-implementation packet itself: one readable-C-anchor question for the diff checker and one absent reminder-side companion.

## Survey result

- The roadmap-backed dual-implementation gap for `scripts/zigux/fixdep.zig` is currently closed on `master`.
- The live repo no longer supports the older survey claim that the fixdep fixture packet stops at twelve external cases. The bounded fixdep packet is now thirteen cases wide and already includes the later dependency-continuation, comment-continuation, and double-backslash-comment parity paths.
- The honest remaining same-family follow-through is smaller than the roadmap survey question: direct contents reads still miss `scripts/basic/fixdep.c` and `Documentation/zigux/artifact-diff.md`, but those misses do not reopen the Phase 2 dual-implementation scaffold gap.
- The honest lane result is therefore a survey-note correction and parking pass, not a new fixdep behavior, fixture, or route implementation.

## Next bounded same-family step

1. Keep `P2-L01` parked unless a fresh current-`master` reread finds new repo-versus-roadmap drift inside the fixdep helper, checker, fixture, or route packet.
2. If the fixdep family reopens, keep the follow-through on a directly coupled non-survey lane: either restore a readable current-`master` C anchor for `scripts/zigux/check-fixdep-diff.py` or re-materialize `Documentation/zigux/artifact-diff.md` as the remaining reminder-surface companion.
3. Do not widen from this survey into genksyms, kconfig, parser behavior, or shared Phase 2 reminder maintenance.
