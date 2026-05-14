# Phase 2 fixdep dual-implementation survey

Lane: `P2-L01`

This note records the current `master` readback for the roadmap-backed `scripts/zigux/fixdep.zig` packet so Phase 2 review stays grounded in the live dual-implementation packet instead of reviving either the older missing-tool story or the stale eleven-case summary.

## Roadmap target

- Phase 2 keeps `scripts/basic/fixdep.c` inside the bounded toolchain tranche.
- The roadmap requires selected dual implementations, and the recommended Zigux destination is `scripts/zigux/fixdep.zig`.
- The bootstrap ledger records both the earlier generic `feat(scripts/zigux): add fixdep dual implementation` milestone and the later narrower bounded fixdep lane with `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/validate-phase2.py`, the committed fixture packet, and the bootstrap workflow route, so the live packet should be judged against that bounded parity posture instead of against a missing scaffold story.

## Current master readback

- `scripts/zigux/fixdep.zig` is present on `master` and already ships a bounded `runFixdep()` entrypoint plus a CLI `main()` wrapper for the direct replay path.
- The live helper-local packet already covers the core bounded parser and error surface: embedded-NUL truncation, escaped whitespace, escaped `#` and `:` tokens, dependency-token continuation across escaped newlines, concatenated target entries, escaped-newline comment skipping, C-style file-read wording, preserved partial stdout on failure, and stdout-write error mapping.
- `zigux/tests/fixtures/fixdep/cases.json` is present and currently names a `12-case` external packet, including `sample_dependency_continuation` and the bounded `/dev/full` write-failure replays `sample_comment_only_stdout_full`, `sample_missing_dep_stdout_full`, and `sample_output_write`.
- `zigux/tests/fixtures/fixdep/sample_dependency_continuation.d` plus `sample_dependency_continuation_expected.txt` prove the escaped-newline dependency-token continuation path as an external artifact packet instead of leaving that behavior helper-local only.
- `scripts/zigux/check-fixdep-diff.py` and `scripts/zigux/check-phase2-fixdep-gate.py` still hard-code the older `11-case` fixdep packet and currently omit `sample_dependency_continuation` from their expected-case inventories.
- `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase2-closure.md`, and `Documentation/zigux/phase2-fixdep-next-step-note.md` still describe the older `eleven-case` fixdep packet, so the dedicated shared reminder surfaces trail the live external fixture packet.
- `scripts/zigux/validate-phase2.py` still reruns `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig`, so the dual-implementation lane remains an active bounded validation packet on current `master`.

## Survey result

- Current `master` does not have a remaining roadmap gap at the level of fixdep dual-implementation scaffolding. The Zig entrypoint, direct replay, external fixture packet, diff checker, and shared validation route are already present.
- The honest remaining gap is smaller and fixdep-local: the shared checkers and reminder notes undercount the live packet by one external case, because `sample_dependency_continuation` is present in the fixtures and aligned with helper-local coverage but not yet reflected in the dedicated fixdep governance surfaces.
- Future reopening in this file family should therefore stay inside fixdep-local packet truthfulness, parity, or validation maintenance, not shared Phase 2 closure churn or revived missing-scaffold narratives.

## Next bounded step

1. Update `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `Documentation/zigux/artifact-diff.md`, and `Documentation/zigux/phase2-fixdep-next-step-note.md` so they model the live `12-case` packet, including `sample_dependency_continuation`.
2. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` so the direct replay and the external artifact packet stay aligned.

## Boundary

Stay inside the `fixdep` lane only. Do not reopen `genksyms`, the kconfig bridge packet, or broader shared Phase 2 reminder work unless a new fixdep-local mismatch proves one of those surfaces directly wrong.
