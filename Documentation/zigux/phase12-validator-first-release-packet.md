# Phase 12 Validator-First Release Packet

This note is the compact PMO companion for the Phase 12 validator-first support bundle on current `master`.

It is a release-planning artifact, not a release-closure claim and not a second direct replay route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared-summary lane owner: `P12-Y07`
- release-readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- release-sequencing companion: `Documentation/zigux/phase12-release-sequencing.md`
- release-coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- release-closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- tests-root companion: `zigux/tests/README.md`
- scripts-root companion: `scripts/zigux/README.md`
- support-bundle checkers: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-cross.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py`
- shared validator route: `scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`

## Shared Order

- keep the validator-first support bundle explicit before the smoke-first replay order: `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- treat `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-cross.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py` as support-bundle evidence rather than as a second direct replay route
- keep the support bundle aligned with `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md`

## Fallback Boundaries

- if `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order through `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`
- do not widen this note into a focused libbpf-only replay, a shared cross-build replay, or a broader shared `check-phase12-*.py` family
- keep `zigux/tests/phase12_build.zig` explicit as the shared smoke-first anchor while the direct `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`

## Next Bounded Step

When the shared Phase 12 packet changes, reread this note beside `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, then refresh only the narrowest support-bundle or release-order wording that drifts next.
