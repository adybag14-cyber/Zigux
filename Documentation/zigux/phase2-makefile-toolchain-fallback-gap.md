# Phase 2 Makefile Toolchain Fallback Gap

This note records one bounded Phase 2 toolchain mismatch on current `master`.

## Why This Matters

The Phase 2 closure packet already says the Linux-style `phase2-toolchain`,
`phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and
`phase2` routes reuse a repo-local `.zig-toolchain` fallback when `ZIG` is
unset. The dedicated pin-scope checker also encodes that broader fallback.

The live `zigux/Makefile` still stops at the pinned channel path only, which
means a repo-local unpacked Zig toolchain can be ignored when the exact pinned
directory is absent.

## Current Repo Evidence

The live `zigux/Makefile` line is:

```make
ZIG_LOCAL_TOOLCHAIN := $(ZIG_PINNED_TOOLCHAIN)
```

The existing Phase 2 pin-scope checker expects:

```make
ZIG_LOCAL_TOOLCHAIN := $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),$(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig)))
```

## Scope Boundary

This gap note is intentionally limited to toolchain selection truthfulness.
It does not reopen Phase 2 fixture inventories, cross-target counts, parser
bridges, or broader kconfig/genksyms behavior.

## Bounded Next Step

Update `zigux/Makefile` so `ZIG_LOCAL_TOOLCHAIN` matches the already-shipped
pin-scope checker and the existing Phase 2 documentation packet, then rerun:

- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-validate`
