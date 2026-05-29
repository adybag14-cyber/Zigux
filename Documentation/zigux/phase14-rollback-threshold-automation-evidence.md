# Phase 14 Rollback Threshold Automation Evidence

This note records the P14-L15 current-master rollback automation readback from 2026-05-29.

## Scope

Lane P14-L15 stays inside the shared Phase 14 rollback-threshold automation packet. It verifies the automation surfaces that keep the core-adjacent packet study-only, reversible, and bounded to the returned `make -C zigux phase14-validate` route.

This note does not promote `phase14-smoke`, `phase14-test`, or aggregate `phase14` Makefile wrappers. Those names remain historical packet vocabulary unless current `master` reintroduces matching routes.

## Current Evidence

Authenticated GitHub contents readback on 2026-05-29 confirmed these current `master` blobs:

- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`: `61e0a58fb28fa0ae9c239c1f03017a48693e5ee2`
- `scripts/zigux/validate-phase14.py`: `c1f45e1b6029c5435c0bcc13b1e45dff9d86d246`
- `scripts/zigux/check-phase14-shared-smoke-route.py`: `540252eeb270d87f1a61f17ec5a076b2c7bb19ed`
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`: `d2d7f587cadb2c479c5acdc2d96c569cf817cbcd`
- `scripts/zigux/check-phase14-rcu-compile-route.py`: `5821a391ea562fbcf9c9c5043786b59fe8acbb25`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`: `0902b0f2d02d18f0208db171f9e4c77af2ee9506`
- `zigux/Makefile`: `b590ef1bb4a3ddd6a817734ee2241442e8935927`
- `.github/workflows/zigux-bootstrap.yml`: `5bdb136b8b6710c08c19566879d5a9da42b63445`
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`: `83793609ada351c5c46b8f2b0b3e2d22b3c59c99`
- `Documentation/zigux/phase14-release-boundary-survey.md`: `f71ef6519a9d9b49a906e8975981dae000df7cf8`
- `Documentation/zigux/phase14-productization-gap-survey.md`: `e3e19371e30804c9373ac0a76e93f24626e9e6cc`
- `scripts/zigux/README.md`: `3143c68d647f9a6d8089ea021676bec198387ea6`

## Automation Contract

The current rollback automation contract is:

- rollback owner: `Repo Tooling Pod`
- status bucket: `study_only`
- rollback threshold: `0` tolerated same-packet drifts
- returned shared route: `make -C zigux phase14-validate`
- workflow route: `.github/workflows/zigux-bootstrap.yml` runs `make -C zigux phase14-validate`
- absent wrappers: `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, and `make -C zigux phase14`
- raw build-file shard remains evidence vocabulary: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`

The current `phase14-validate` route runs the shared route checker, tests-root reminder checker, validator, rollback-threshold sequencing checker, skbuff stay-in-C guardrail, RCU rollback guardrail, and release-boundary exact-count checker. The validator also fail-closes on the skbuff, ring-buffer, and RCU compile-route checkers, so those compile-route booleans are part of the rollback automation evidence without becoming separate Makefile wrappers.

## Exact Drift Triggers

The rollback-threshold sequencing checker currently names these automatic return-to-blocked triggers:

- recovered documentation packet drift
- route-checker-versus-reminder-surface drift
- tests-root-checker-versus-reminder-surface drift
- validator-versus-reminder-surface drift
- rollback-threshold-sequencing drift
- dedicated-skbuff-stay-in-c-guard drift
- dedicated-skbuff-compile-route-guard drift
- dedicated-ring-buffer-compile-route-guard drift
- dedicated-rcu-rollback-guard drift
- workqueue-boundary-shard drift
- ring-buffer-survey drift
- dedicated-rcu-survey drift
- wrapper-route drift
- build-side exact-readback-gap drift
- broader executable-layer exact-readback-gap drift
- attached-toolchain guidance drift inside the shared smoke note

## Verification Result

The P14-L15 verification found the rollback automation active and bounded. No anchor-local Phase 14 ownership changed, no broader Phase 14 wrapper route was promoted, and no parity claim was added.

The next same-lane check should reread the files above first. If they drift, repair the smallest shared rollback-threshold evidence surface before touching shared smoke prose, compile-shard matrix notes, or anchor-local Phase 14 packets.
