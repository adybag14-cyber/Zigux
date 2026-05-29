# Phase 11 Helper Parity Matrix Current Behavior Evidence

This note records the exact current-head evidence for lane `P11-L03`: verifying the shared Phase 11 helper-parity / validation-matrix behavior without widening into driver-local execution claims.

## Scope

- Lane: `P11-L03`
- Phase: `Phase 11`
- Roadmap anchor: simple production drivers require a hardware validation matrix plus teardown and failure-mode parity for `gpio_wdt`, `bcm2835_wdt`, `dw_wdt`, and `hvc_console`.
- Current shared packet: `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- Evidence mode: authenticated GitHub contents rereads on current `master`, plus current checker and fixture behavior recorded below.

## Current Reread Evidence

The current shared survey blob reread for this lane is:

- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`: `5a87bfc5c5d996cc6198681d400ec5793493b16b`

The survey currently records:

- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`
- the shared packet lane as `P11-Y06`
- the deterministic tooling survey lane as `P11-L07`
- the four driver-local matrix notes as present on current `master`:
  - `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
  - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`

The survey also keeps the focused teardown-or-failure-mode proof builds explicit rather than collapsing the shared packet into matrix presence alone:

- `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- `zigux/tests/phase11_dw_wdt_restart_build.zig`
- `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig`

## Checker Behavior Evidence

The current lightweight survey checker blob reread for this lane is:

- `scripts/zigux/check-phase11-matrix-gap-survey.py`: `58ad4965d1a714c48b22b886f89cc69b3da7e3f1`

That checker currently requires the shared survey to retain:

- the `all_simple_driver_matrices_present` status
- the returned four-matrix roster
- the current deterministic fixture surface list
- the `3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays` count
- the focused HVC direct-build pair
- the focused watchdog teardown-or-failure-mode proof pair
- the dedicated HVC cleanup-current-head and targetless-unregister witness checker routes
- the live `make -C zigux phase11-validate` route
- per-driver wording for bcm2835, gpio, and DesignWare matrix rereads

It also fail-closes on stale older claims that would say the driver-local matrix roster is incomplete on current `master`. Its self-test behavior is expected to print:

```text
PHASE11_MATRIX_GAP_SURVEY_SELF_TEST=pass
PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=24
```

The stricter cross-surface checker blob reread for this lane is:

- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`: `2ec8d6d2db9f3992cf8dcacfb7418ed780c72676`

That checker currently validates the shared survey against all of these surfaces together:

- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/fixtures/phase11_validate_checks.json`
- `scripts/zigux/validate-phase11.py`
- `zigux/Makefile`

Its current behavior requires:

- exact survey markers for the roadmap anchor, four matrix notes, deterministic fixture surfaces, focused teardown-or-failure-mode proof builds, and the remaining golden-output tooling gap
- exact inventory list values for `build_test_names`, `shared_test_depend_steps`, `dedicated_survey_replays`, `shared_adjunct_replays`, `shared_adjunct_build_replays`, `focused_direct_build_replays`, `deterministic_fixture_surfaces`, and `focused_teardown_failure_mode_builds`
- exact inventory scalar values for `deterministic_tooling_lane` and `deterministic_golden_output_gap`
- exact `validate-phase11.py` markers for the four focused teardown-or-failure-mode build checks
- exact `zigux/Makefile` command markers for the same four focused build checks
- exact `phase11_validate_checks.json` entries for `phase11-validation-matrix-gap-survey-self-test` and `phase11-validation-matrix-gap-survey`

Its self-test now iterates over every `SURVEY_MARKERS` entry instead of only the first seven survey markers, so stale roadmap-anchor, four-matrix roster, deterministic-tooling-gap, or review-boundary wording should all fail the fixture replay. Its self-test behavior is expected to print:

```text
PHASE11_MATRIX_GAP_SURVEY_CHECK=pass
PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=23
```

## Fixture Evidence

The current shared build inventory blob reread for this lane is:

- `zigux/tests/fixtures/phase11_build_inventory.json`: `86bdd83a4fc8544c09ba7f0f6cedb8685700f59c`

The current inventory behavior is:

- `build_test_names`: 3 HVC proof-backed build tests
- `shared_test_depend_steps`: 0 entries
- `dedicated_survey_replays`: 0 entries
- `shared_adjunct_replays`: 3 proof adjunct replays
- `shared_adjunct_build_replays`: 3 adjunct build replays
- `focused_direct_build_replays`: 2 HVC focused direct build replays
- `focused_teardown_failure_mode_builds`: 4 total focused teardown-or-failure-mode build replays, split across HVC, DesignWare, and gpio watchdog
- `deterministic_tooling_lane`: `P11-L07`

The current validate-check roster blob reread for this lane is:

- `zigux/tests/fixtures/phase11_validate_checks.json`: `4cb91d32b0257c2b38653c0c3f01408d19f288ff`

That roster currently includes the two shared matrix-gap checks and the stricter validation-matrix-gap checks:

- `phase11-matrix-gap-survey-self-test`
- `phase11-matrix-gap-survey`
- `phase11-validation-matrix-gap-survey-self-test`
- `phase11-validation-matrix-gap-survey`

It also includes focused build commands for the four teardown-or-failure-mode proof builds named above.

## Verified Behavior Boundary

The current parity-matrix behavior is matrix-roster-present and build-proof-first:

- current `master` keeps the four driver-local matrix notes named by the Phase 11 roadmap explicit
- current `master` keeps focused teardown-or-failure-mode proof builds visible beside the matrix roster
- current `master` has machine-readable inventory and validate-check fixtures for the shared packet
- current `master` has checkers that fail-close on stale matrix-roster wording, inventory drift, validate-route drift, Makefile command drift, missing shared matrix-gap check entries, and any omitted strict survey marker in the validation-matrix-gap replay fixture

The current packet still does not provide a refresh helper route or artifact-diff-style deterministic output comparison for the driver-local proof builds. That is the exact remaining behavior boundary: `phase11-validate` proves the current shared packet through checkers and build replays, but it does not yet refresh and diff stable expected-output artifacts for the Phase 11 proof fan-out.
