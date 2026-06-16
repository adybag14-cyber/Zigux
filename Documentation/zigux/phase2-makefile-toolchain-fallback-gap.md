# Phase 2 Makefile Toolchain Fallback Gap

**Status: resolved on current `master`.**

The live `zigux/Makefile` now selects a repo-local `.zig-toolchain` fallback when the
exact pinned extract directory is absent:

```make
ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))
ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))
```

This matches the Phase 2 pin-scope checker and the shipped documentation packet.

## Verification

- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-validate`
- `zig test scripts/zigux/toolchain_policy.zig`