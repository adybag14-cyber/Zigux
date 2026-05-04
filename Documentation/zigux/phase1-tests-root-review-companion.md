# Phase 1 Tests-Root Review Companion

This note keeps the tests-root view of the closed Phase 1 host-helper packet reviewable without reopening the broader helper tranche.

## Shared reviewer surface

The closed Phase 1 packet should continue to agree across these shared review surfaces:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase1-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

## Tests-root ownership

From the tests root, the bounded Phase 1 packet is carried by:
- `zigux/tests/build.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_helpers.json`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
- `zigux/tests/fixtures/phase1_bench_expectations.json`

Those files should keep the closed helper inventory, the harness-backed parity replay surface, the replay entrypoints, the benchmark checksum contract, and the helper-review notes aligned with the docs-root and scripts-root packet.

## Validator-first route

The tests-root packet stays bounded behind the same validator-first route:
- `python3 scripts/zigux/validate-phase1.py`
- `python3 scripts/zigux/validate-phase1-closure.py`
- `make -C zigux phase1-validate`
- `make -C zigux phase1-test`
- `make -C zigux phase1-bench`
- `make -C zigux phase1`

The dedicated fail-closed checker stack remains explicit through these self-tests and live gates:
- `python3 scripts/zigux/validate-phase1.py --self-test`
- `python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test`
- `python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py`
- `python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test`
- `python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py`
- `python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test`
- `python3 scripts/zigux/check-phase1-route-summary-counts.py`
- `python3 scripts/zigux/check-phase1-validation-route-inventory.py --self-test`
- `python3 scripts/zigux/check-phase1-validation-route-inventory.py`
- `python3 scripts/zigux/check-phase1-parity.py --self-test`
- `python3 scripts/zigux/check-phase1-parity.py`
- `python3 scripts/zigux/check-phase1-bench.py --self-test`
- `python3 scripts/zigux/check-phase1-bench.py`
- `python3 scripts/zigux/validate-phase1-closure.py --self-test`
- `python3 scripts/zigux/validate-phase1-closure.py`

## Review rule

If a change touches the closed Phase 1 helper packet, update this companion only when the tests-root ownership view or the shared reviewer surface changes too. Keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-validation-route-inventory.py`, `scripts/zigux/validate-phase1-closure.py`, and `zigux/tests/README.md` aligned when that shared tests-root review packet changes. Do not treat a new helper, a new alias family, or a widened runtime claim as Phase 1 maintenance unless the dedicated closure packet is deliberately reopened.
