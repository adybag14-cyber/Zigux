# Phase 2 fixdep next step note

Lane: `P2-L06`

Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor, and the live fixdep governance packet remains broader and healthier than older reminder wording suggested.

## Roadmap and ledger grounding

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records the bounded fixdep tranche around `scripts/zigux/fixdep.zig` together with parity-companion and workflow-backed follow-through, so the family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/fixdep.zig`, `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/validate-phase2.py`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, `Documentation/zigux/phase2-fixdep-next-step-note.md`, `Documentation/zigux/artifact-diff.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zigux/tests/README.md`, and `zigux/tests/fixtures/fixdep/cases.json`.
- `scripts/zigux/fixdep.zig` now carries twenty-three helper-local tests covering CONFIG token trimming, prefixed-token rejection, punctuation and embedded-NUL handling, comment-only depfiles, escaped-space and escaped-newline parsing, CRLF and bare-carriage-return behavior, read-error wording, larger-than-legacy depfiles, and the escaped hash or colon comment-path survivors.
- `zigux/tests/fixtures/fixdep/cases.json` currently inventories 13 external fixdep cases, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_double_backslash_comment`, and the current stdout-failure replay cases.
- The live bootstrap workflow and `zigux/Makefile` still expose direct fixdep replay routes through `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py`, `make -C zigux phase2-fixdep`, and `zig test scripts/zigux/fixdep.zig`.
- The shared closure note and tests-root reminder both keep the fixdep helper, checker pair, fixture roster, and wrapper route explicit as current repo evidence.
- Repeated exact-path contents reads still return missing for `scripts/basic/fixdep.c`, but the live parity checker no longer pins that C path directly and instead stays bounded to `scripts/zigux/fixdep.zig`, `Documentation/zigux/artifact-diff.md`, and the committed fixture packet.

## Survey result

- The older same-lane reminder drift around supposedly missing fixdep governance, wrapper, and fixture coverage is now closed by current repo evidence.
- The current diff-and-artifact packet is truthful again: `scripts/zigux/check-fixdep-diff.py` now validates the Zig helper path, the thirteen-case fixture roster, the committed expected-output files, and deterministic repeat runs without depending on a readable `scripts/basic/fixdep.c` path.
- The live helper-local test surface is also broad enough that this lane does not currently have an honest parser-side or expected-output-side reopen signal.
- Widening this lane into parser behavior, expected-output growth, or shared Phase 2 reminder maintenance would skip over the honest current result, which is to keep the lane parked until a fresh fixdep-local failure appears.

## Next safe step

1. Keep `P2-L06` parked unless a fresh current-`master` reread finds new drift inside the live fixdep helper, checker, fixture, or route packet.
2. If the fixdep family reopens, start with one smallest same-family follow-through only: prefer a new direct mismatch in `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `Documentation/zigux/artifact-diff.md`, or `zigux/tests/fixtures/fixdep/cases.json` before reopening parser behavior or adding another expected-output packet.
3. Do not widen from this reminder lane into parser behavior, fixture expected outputs, genksyms, kconfig bridge, or the broader shared Phase 2 route inventory without a new direct fixdep failure signal.