# Phase 2 fixdep next step note

Lane: `P2-X02`

Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor, but the surviving fixdep companion packet is now narrower and split differently than older closure notes claimed.

## Roadmap and ledger grounding

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records the bounded fixdep tranche around `scripts/zigux/fixdep.zig` together with parity-companion and workflow-backed follow-through, so the family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` still directly serves `scripts/zigux/fixdep.zig`, so the core dual-implementation helper remains real rather than speculative.
- Current `master` also directly serves `scripts/zigux/check-phase2-fixdep-gate.py`, `Documentation/zigux/phase2-closure.md`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and this note.
- Repeated direct reads on current `master` still return missing for `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, and `Documentation/zigux/artifact-diff.md`, so the older note about a fully materialized external fixdep parity packet is no longer truthful on current head.
- The live bootstrap workflow and `zigux/Makefile` no longer show dedicated fixdep replay routes, so the surviving dedicated gate script is present but not currently backed by the older shared wrapper and workflow path.

## Survey result

- The same-lane gap is now closure-note drift, not helper-local parser drift.
- `scripts/zigux/fixdep.zig` and `scripts/zigux/check-phase2-fixdep-gate.py` still make the fixdep family directly readable on current `master`, but the broader external fixture roster and artifact-diff companions recorded by older notes are not currently materialized.
- Because that external parity packet is still partial, the next honest move is to correct the closure packet first instead of pretending the full older replay stack still exists.

## Next safe step

1. Choose one exact same-family repair: either narrow `scripts/zigux/check-phase2-fixdep-gate.py` so it only pins the live closure surfaces that still carry fixdep evidence, or re-materialize one smallest missing external parity companion such as `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, or `Documentation/zigux/artifact-diff.md`.
2. Only after that fixdep-local companion packet is truthful again should follow-through widen into shared reminder surfaces such as the workflow, scripts-root README, or Makefile wording.
3. Keep this lane inside fixdep only; do not widen into genksyms, kconfig, or general Phase 2 route inventory.
