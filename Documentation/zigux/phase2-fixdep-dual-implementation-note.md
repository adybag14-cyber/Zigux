# Phase 2 Fixdep Dual-Implementation Note

This note keeps the live `scripts/zigux/fixdep.zig` packet honest against the Phase 2 roadmap and the current repo state.

## Current direct packet

- `scripts/zigux/fixdep.zig` is directly readable on current `master` and remains a real bounded Phase 2 dual-implementation anchor under the roadmap's toolchain and Kbuild enablement tranche.
- The live Zig helper still carries the current parser and output-shaping proof points visible from the file itself, including `_MODULE` trimming in config-token handling, escaped-space and escaped-colon dep parsing, comment-only and concatenated-target handling, embedded-NUL truncation, large depfile reads beyond the old one-mebibyte ceiling, and C-style read or write error wording.
- `.github/workflows/zigux-bootstrap.yml` is directly readable on current `master` and currently moves from the shared Phase 2 toolchain and kconfig checks to later phases without a dedicated fixdep checker or direct `zig test scripts/zigux/fixdep.zig` replay step.

## Current repo-reality gaps

- Repeated authenticated reads on current `master` still return missing for `scripts\zigux/check_fixdep_diff.zig`, `scripts\zigux/check_phase2_fixdep_gate.zig`, `Documentation/zigux/phase2-closure.md`, `scripts\zigux/validate_phase2.zig`, and `scripts\zigux/validate_phase2_closure.zig`.
- Treat those parity-checker, gate-checker, closure-side, and validator-first names as missing current packet companions rather than as directly readable shipped evidence.
- `scripts/zigux/README.md`, `Documentation/zigux/README.md`, and `zigux/tests/README.md` currently summarize Phase 2 around the surviving toolchain, kbuild, and kconfig bridge packet, so they do not yet expose this live fixdep helper anchor from their shared reminder surfaces.

## Follow-through

- Keep future fixdep follow-up inside one current packet surface at a time: helper-local parser or unit-test proof in `scripts/zigux/fixdep.zig`, a rematerialized parity or gate checker, or workflow-local replay restoration.
- Do not widen this note into genksyms parser behavior, kconfig bridge semantics, or broader Phase 2 toolchain policy work.
- If the missing fixdep checker or workflow packet returns on current `master`, refresh this note only after rereading `scripts/zigux/fixdep.zig`, `.github/workflows/zigux-bootstrap.yml`, and the new companion paths together.