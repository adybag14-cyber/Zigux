# Phase 2 Toolchain Bootstrap Notes

This note records the bounded Phase 2 x86_64-linux bootstrap archive-pin contract.

- policy file: `scripts/zigux/zig-toolchain-policy.json`
- guard self-test: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- guard: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- workflow installer self-test: `python3 scripts/zigux/install-zig.py --self-test`
- workflow verifier self-test: `python3 scripts/zigux/check-zig-toolchain.py --self-test`
- compile-matrix self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`
- compile-matrix guard: `python3 scripts/zigux/check-phase2-cross.py`
- shared genksyms bridge selftest-alignment self-test: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`
- shared genksyms bridge selftest-alignment guard: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`
- shared genksyms CRC parity gate: `python3 scripts/zigux/check-genksyms-crc-diff.py`
- shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- shared kconfig selftest-alignment guard: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- shared kconfig bridge self-test: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- shared kconfig bridge parity gate: `python3 scripts/zigux/check-kconfig-bridge.py`
- shared tests README alignment gate: `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`
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
- current pinned bootstrap archive sha256 (`x86_64-linux`): `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`
- the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence
- the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin
- the shared tests README alignment gate keeps this dedicated bootstrap note aligned with `zigux/tests/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/Makefile`, and the Linux-style `make -C zigux phase2-validate`, `make -C zigux phase2-kconfig`, and `make -C zigux phase2` replay surface instead of leaving this note coupled to the broader Phase 2 packet by implication alone
- `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`, and `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py` keep `Documentation/zigux/phase2-closure.md`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned around that three-target compile matrix without broadening the pinned bootstrap archive beyond `x86_64-linux`
- `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test` and `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py` keep this bootstrap note aligned with the already-shipped `check-genksyms-bridge.py` route, the workflow-backed self-test plus live guard, and the bounded `genksyms.zig` bridge packet so that surface stays visible beside the archive pin instead of being implied only by closure-only surfaces
- `python3 scripts/zigux/check-genksyms-crc-diff.py` keeps this bootstrap note aligned with the already-shipped workflow-backed parity replay, the `phase2-tools` Makefile lane, and the bounded direct `zig test scripts/zigux/genksyms_crc.zig` replay so the dedicated `genksyms_crc.zig` helper surface stays visible beside the archive pin instead of living only in the closure record
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test` and `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py` keep this bootstrap note aligned with the already-shipped `check-kconfig-bridge.py` self-test plus live guard, the Phase 2 closure record, the `phase2-kconfig` Makefile lane, and the bounded `zig test scripts/zigux/kconfig/conf_bridge.zig` plus `zig test scripts/zigux/kconfig/confdata_bridge.zig` replays so the bounded kconfig bridge packet stays visible beside the archive pin instead of being implied only by closure-only surfaces
- the shared and closure validators above, together with `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, are the fail-closed route that keeps this note in the bounded Phase 2 toolchain tranche instead of leaving it as stand-alone reference text
- the Linux-style `make -C zigux phase2-validate`, `make -C zigux phase2-kconfig`, and `make -C zigux phase2` routes keep the dedicated note tied to the same kbuild-facing replay surface named by the docs-root summary, the shared validators, the closure note, and the shared review checklist
