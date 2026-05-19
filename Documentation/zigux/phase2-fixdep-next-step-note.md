# Phase 2 fixdep next step note

Lane: `P2-L01`

Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor, but the broader external parity packet described by older fixdep notes is no longer directly materialized on current head.

## Roadmap and ledger grounding

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records the bounded fixdep tranche around `scripts/zigux/fixdep.zig` together with a parity checker, validator entrypoint, fixture packet, and workflow-backed replay.

## Current repo evidence

- Current `master` still directly serves `scripts/zigux/fixdep.zig`, so the core dual-implementation helper remains real rather than speculative.
- Current `master` also directly serves `.github/workflows/zigux-bootstrap.yml`, `scripts/zigux/README.md`, `Documentation/zigux/phase2-closure.md`, and this note, and those shared surfaces now describe a narrower surviving Phase 2 packet centered on the kconfig bridges, toolchain pinning, and closure-side validators.
- Repeated direct reads on current `master` now return missing for `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/check-phase2-fixdep-gate.py`, `zigux/tests/fixtures/fixdep/cases.json`, and `Documentation/zigux/artifact-diff.md`, so the older note about a live twelve-case external fixdep packet is no longer truthful on current head.
- The live bootstrap workflow no longer shows dedicated fixdep parity or direct `zig test scripts/zigux/fixdep.zig` steps, which matches that narrower current-head packet rather than the older fixdep-specific replay story.

## Survey result

- The same-lane gap is now repo-reality drift, not helper-local parser drift.
- `scripts/zigux/fixdep.zig` still satisfies the roadmap's selected dual-implementation anchor, but the directly readable checker, fixture, and closure companions recorded in older fixdep notes are no longer present on current `master`.
- Because those companions are absent, the next honest move is not to add another external fixture case on top of a non-materialized packet.

## Next safe step

1. Re-materialize the smallest current-head fixdep companion packet first: one direct parity checker or one committed fixture roster that current `master` can actually read beside `scripts/zigux/fixdep.zig`.
2. Only after that companion packet returns should follow-through widen into shared reminder surfaces such as the workflow, scripts-root README, or closure note.
3. Keep this lane inside fixdep only; do not widen into genksyms, kconfig, or general Phase 2 route inventory.
