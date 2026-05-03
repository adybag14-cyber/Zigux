# Phase 2 Toolchain Bootstrap Notes

This note records the bounded Phase 2 bootstrap archive-pin contract.

- policy file: `scripts/zigux/zig-toolchain-policy.json`
- guard self-test: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- guard: `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`
- workflow install path: `python3 scripts/zigux/install-zig.py --dest .zig-toolchain`
- workflow verification path: `python3 scripts/zigux/check-zig-toolchain.py`
- current pinned bootstrap archive target: `x86_64-linux`
- the archive pin must stay limited to `x86_64-linux` until a new bootstrap runner target gains first-class workflow evidence