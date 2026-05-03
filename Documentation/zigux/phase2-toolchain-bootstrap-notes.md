# Phase 2 Toolchain Bootstrap Notes

This note records the bounded Phase 2 bootstrap archive-pin contract.

- policy file: `scripts/zigux/zig-toolchain-policy.json`
- guard self-test: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- guard: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- workflow install path: `python3 scripts/zigux/install-zig.py --dest .zig-toolchain`
- workflow verification path: `python3 scripts/zigux/check-zig-toolchain.py`
- current pinned Zig channel: `0.17.0-dev.87+9b177a7d2`
- current minimum Zig version: `0.17.0-dev.87+9b177a7d2`
- current pinned bootstrap archive target: `x86_64-linux`
- the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence
- the three-target compile matrix in `zigux/tests/fixtures/phase2_cross_targets.json` stays separate from the `x86_64-linux` bootstrap archive pin
