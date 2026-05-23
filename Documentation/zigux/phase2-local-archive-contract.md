# Phase 2 Local Archive Contract

`third_party/README.md`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` remain the current direct-readback anchors for the pinned archive contract, the local-first `third_party`, mirror, then direct-download bootstrap order, and the shipped Lane 05 reminder guards.

`scripts/zigux/check-phase2-local-archive-contract.py` keeps this focused Phase 2 note fail-closed against current repo reality: when `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` is still absent it requires the missing-tolerant `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay, and it only allows the exact archive-path replay back into this note after that pinned payload lands on current `master`.

current `master` still does not materialize `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, so keep the repo-local archive wording tied to `third_party/README.md`, the two Lane 05 reminder guards, and the missing-tolerant `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` replay until that pinned payload actually lands.
