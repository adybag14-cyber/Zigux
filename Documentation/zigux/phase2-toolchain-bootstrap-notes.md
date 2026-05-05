# Phase 2 Toolchain Bootstrap Notes

This note records the bounded Phase 2 bootstrap archive-pin contract.

- policy file: `scripts/zigux/zig-toolchain-policy.json`
- guard self-test: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- guard: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- workflow installer self-test: `python3 scripts/zigux/install-zig.py --self-test`
- workflow verifier self-test: `python3 scripts/zigux/check-zig-toolchain.py --self-test`
- cross-matrix self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`
- cross-matrix gate: `python3 scripts/zigux/check-phase2-cross.py`
- tests-root alignment self-test: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`
- tests-root alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`
- shared validator gate: `python3 scripts/zigux/validate-phase2.py`
- closure validator gate: `python3 scripts/zigux/validate-phase2-closure.py`
- closure note: `Documentation/zigux/phase2-closure.md`
- docs-root summary: `Documentation/zigux/README.md`
- shared review checklist: `Documentation/zigux/review-checklist.md`
- workflow install path: `python3 scripts/zigux/install-zig.py --dest .zig-toolchain`
- workflow verification path: `python3 scripts/zigux/check-zig-toolchain.py`
- current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`
- current minimum Zig version: `0.17.0-dev.87+9b177a7d2`
- current pinned bootstrap archive target: `x86_64-linux`
- current pinned bootstrap archive sha256 (`x86_64-linux`): `a3eae1cdb9643cf68e09e97574fb6780699e05148c270e52347faa293b80d858`
- the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence
- the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test` and `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py` keep `Documentation/zigux/README.md`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around that three-target compile matrix without broadening the pinned bootstrap archive beyond `x86_64-linux`
- `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test` and `python3 scripts/zigux/check-phase2-tests-readme-alignment.py` keep `zigux/tests/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around the same three-target compile matrix, validator pair, and Linux-style `make -C zigux phase2-validate` plus `make -C zigux phase2` replay surface
- `python3 scripts/zigux/validate-phase2.py` now runs `python3 scripts/zigux/check-phase2-tests-readme-alignment.py` before the toolchain pin-scope guard, so tests-root compile-matrix drift fails inside the shared validator route instead of relying on review-only notice
- the shared and closure validators above, together with `Documentation/zigux/review-checklist.md`, are the fail-closed route that keeps this note in the bounded Phase 2 toolchain tranche instead of leaving it as stand-alone reference text
- the Linux-style `make -C zigux phase2-validate` and `make -C zigux phase2` routes keep the dedicated note tied to the same kbuild-facing replay surface named by the shared validators, the closure note, and the shared review checklist
