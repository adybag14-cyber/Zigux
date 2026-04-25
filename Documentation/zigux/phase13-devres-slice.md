# Phase 13 devres Slice

This bounded Phase 13 slice starts `lib/devres.zig` with a pure helper-first foothold anchored to `lib/devres.c`.

The current helper stays intentionally narrow:

- exposes module metadata for the `lib/devres.c` anchor and keeps the lane explicitly reviewable
- models the managed `__devm_ioremap()` release-record lifetime decision so the helper can distinguish successful retention from free-on-failure cleanup
- keeps the release action pinned to `iounmap` and mirrors the pointer-exact match rule used by `devm_iounmap()`

This slice does not claim live device-list mutation, `devres_alloc_node()` ownership, MMIO mapping calls, resource-region requests, pretty-name allocation, or any other side effects from the wider `lib/devres.c` body.

The next honest bounded step in this same lane is to stay helper-first and add one small managed token or memory-range release helper next, still avoiding live device bookkeeping and MMIO side effects.
