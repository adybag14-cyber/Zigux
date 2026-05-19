# Phase 2 fixdep dual-implementation survey

Lane: `P2-L01`

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records a bounded fixdep lane around `scripts/zigux/fixdep.zig` together with parity-companion and workflow-backed follow-through, so this family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` still directly serves `scripts/zigux/fixdep.zig`, so the core dual-implementation helper remains present on head.
- Current `master` also directly serves `scripts/zigux/check-phase2-fixdep-gate.py`, which keeps one dedicated fixdep-local governance surface materialized beside the helper.
- Current `master` now again directly serves the broader Phase 2 installer and cross-route packet through `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/README.md`, and `zigux/tests/fixtures/phase2_tool_manifest.json`.
- Repeated direct reads on current `master` still return missing for `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, and `Documentation/zigux/artifact-diff.md`, so the older picture of a fully materialized dedicated fixdep parity packet is no longer truthful on current head.
- The live `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` no longer expose dedicated fixdep replay routes, which means the current Phase 2 shared wrapper packet is broader than fixdep and no longer advertises the older fixdep-specific replay stack.

## Survey result

- The roadmap-backed dual-implementation anchor still exists: `scripts/zigux/fixdep.zig` is present and reviewable on current `master`.
- The repo gap versus the roadmap is no longer “fixdep missing”; it is that the dedicated fixdep companion packet is only partially materialized on current head.
- The current truthful fixdep packet is the helper itself plus the surviving gate checker, while the older diff-checker, fixture-roster, and artifact-diff companions remain absent.
- The surrounding Phase 2 support packet has moved forward through returned installer and direct cross-route surfaces, so fixdep survey work should not keep describing those broader companions as missing.

## Next bounded same-family step

1. Keep `P2-L01` parked unless the survey itself drifts again against current `master`.
2. Let the next fixdep-local follow-through stay with the deterministic-check or closure-correction lane: either narrow `scripts/zigux/check-phase2-fixdep-gate.py` to the surviving fixdep packet or re-materialize one smallest missing fixdep-specific companion such as `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, or `Documentation/zigux/artifact-diff.md`.
3. Do not widen from this survey into genksyms, kconfig, or general Phase 2 reminder maintenance.
