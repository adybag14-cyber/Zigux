# Phase 2 fixdep next step note

Lane: `P2-L06`

Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor, and the live fixdep governance packet remains broader and healthier than older reminder wording suggested.

## Roadmap and ledger grounding

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records the bounded fixdep tranche around `scripts/zigux/fixdep.zig` together with parity-companion and workflow-backed follow-through, so the family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/fixdep.zig`, `scripts\zigux/check_phase2_fixdep_gate.zig`, `scripts\zigux/check_fixdep_diff.zig`, `scripts\zigux/validate_phase2.zig`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, `Documentation/zigux/phase2-fixdep-next-step-note.md`, `Documentation/zigux/artifact-diff.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zigux/tests/README.md`, and `zigux/tests/fixtures/fixdep/cases.json`.
- `scripts/zigux/fixdep.zig` now carries twenty-six helper-local tests covering CONFIG token trimming, prefixed-token rejection, punctuation and embedded-NUL handling, comment-only depfiles, escaped-space and escaped-newline parsing, CRLF and bare-carriage-return behavior, read-error wording, larger-than-legacy depfiles, flush-primary-error preservation, escaped hash or colon comment-path survivors, the CRLF escaped-colon survivor, and a public `runFixdep` entry-path replay for escaped-colon dependencies.
- `zigux/tests/fixtures/fixdep/cases.json` currently inventories 13 external fixdep cases, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_double_backslash_comment`, and the current stdout-failure replay cases.
- The live bootstrap workflow and `zigux/Makefile` still expose direct fixdep replay routes through `zig run scripts/zigux/check_phase2_fixdep_gate.zig`, `zig run scripts/zigux/check_fixdep_diff.zig`, `make -C zigux phase2-fixdep`, and `zig test scripts/zigux/fixdep.zig`.
- The shared closure note and tests-root reminder both keep the fixdep helper, checker pair, fixture roster, and wrapper route explicit as current repo evidence.
- Repeated exact-path contents reads still return missing for `scripts/basic/fixdep.c`, but the live parity checker no longer pins that C path directly and instead stays bounded to `scripts/zigux/fixdep.zig`, `Documentation/zigux/artifact-diff.md`, and the committed fixture packet.

## Survey result

- The older same-lane reminder drift around supposedly missing fixdep governance, wrapper, and fixture coverage is now closed by current repo evidence.
- The direct Phase 2 gate is truthful again: `scripts\zigux/check_phase2_fixdep_gate.zig` now pins twenty-six named helper-local tests, including the CRLF escaped-colon concatenated-target survivor and `test "runFixdep preserves escaped colon dependencies through the public entry path" {`, alongside the live workflow, Makefile, fixture, and closure markers.
- The current diff-and-artifact packet is truthful again: `scripts\zigux/check_fixdep_diff.zig` now validates the Zig helper path, the thirteen-case fixture roster, the committed expected-output files, and deterministic repeat runs without depending on a readable `scripts/basic/fixdep.c` path.
- The live helper-local test surface is broad enough that this lane does not currently have an honest parser-side, gate-roster-side, or expected-output-side reopen signal.
- Widening this lane into parser behavior, expected-output growth, or shared Phase 2 reminder maintenance would skip over the honest current result, which is to keep the lane parked until a fresh fixdep-local failure appears.

## Next safe step

1. Keep `P2-L06` parked unless a fresh current-`master` reread finds new drift inside the live fixdep helper, checker, fixture, route, or reminder packet.
2. If the fixdep family reopens, start with one smallest same-family follow-through only: prefer a new direct mismatch in `scripts\zigux/check_fixdep_diff.zig`, `scripts\zigux/check_phase2_fixdep_gate.zig`, `Documentation/zigux/artifact-diff.md`, `zigux/tests/fixtures/fixdep/cases.json`, or the direct Phase 2 route surfaces before reopening parser behavior or adding another expected-output packet.
3. If `scripts/zigux/fixdep.zig` grows another helper-local test, first teach `scripts\zigux/check_phase2_fixdep_gate.zig` about that exact new test line so the gate roster stays aligned with the helper surface.
4. Do not widen from this reminder lane into parser behavior, fixture expected outputs, genksyms, kconfig bridge, or the broader shared Phase 2 route inventory without a new direct fixdep failure signal.
