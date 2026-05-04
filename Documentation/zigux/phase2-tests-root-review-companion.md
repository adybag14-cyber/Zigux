# Phase 2 Tests-Root Review Companion

This note keeps the tests-root view of the closed Phase 2 toolchain and kbuild packet reviewable without reopening the broader bootstrap tranche.

## Shared reviewer surface

The closed Phase 2 packet should continue to agree across these shared review surfaces:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

## Tests-root ownership

From the tests root, the bounded Phase 2 packet is carried by:
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/fixdep/`
- `zigux/tests/fixtures/genksyms_bridge/`
- `zigux/tests/fixtures/kconfig_bridge/`

Those fixture packets should keep the bounded tool inventory, the direct three-target compile matrix, the shared artifact-diff parity corpus, and the wrapper-first bridge evidence aligned with the docs-root and scripts-root packet.

## Bootstrap-versus-cross boundary

The tests-root packet should continue to keep the current Phase 2 bootstrap boundary explicit:
- `scripts/zigux/zig-toolchain-policy.json` keeps the bootstrap archive pin limited to `x86_64-linux`.
- `zigux/tests/fixtures/phase2_cross_targets.json` keeps the separate direct compile matrix explicit for `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl`.
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-cross.py`, and `scripts/zigux/check-phase2-cross-selftest-alignment.py` should keep that bounded archive-pin-versus-cross-matrix split reviewable from the same Phase 2 packet.

## Validator-first route

The tests-root packet stays bounded behind the same validator-first route:
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `python3 scripts/zigux/check-phase2-cross.py --self-test`
- `python3 scripts/zigux/check-phase2-cross.py`
- `python3 scripts/zigux/validate-phase2.py`
- `python3 scripts/zigux/validate-phase2-closure.py`
- `make -C zigux phase2-validate`
- `make -C zigux phase2-cross`
- `make -C zigux phase2`

## Review rule

Update this companion only when the tests-root ownership view, the bootstrap-pin-versus-cross-matrix boundary, or the validator-first Phase 2 route changes too. Do not treat a wider bootstrap runner target, a new parser-heavy replacement claim, or a broader kbuild rewrite as Phase 2 maintenance unless the dedicated closure packet is deliberately reopened with matching docs, tests, and review-surface evidence.
