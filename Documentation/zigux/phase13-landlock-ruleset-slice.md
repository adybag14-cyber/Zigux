# Phase 13 Landlock Ruleset Slice

This bounded Phase 13 slice starts `security/landlock/ruleset.zig` with a pure helper-first foothold anchored to `security/landlock/ruleset.c`.

The current helper stays intentionally narrow:

- models the empty-ruleset rejection and single-layer initialization path of `landlock_create_ruleset()` without claiming allocation, mutex setup, refcounts, or anonymous-fd plumbing
- unions filesystem, network, and scope access masks across a layer stack so the lane can describe the handled-access summary that later ruleset and domain checks rely on
- mirrors the per-layer request initialization done by `landlock_init_layer_masks()`, including the always-denied-by-default filesystem access bit when any filesystem mask is active
- captures the `landlock_unmask_layers()` bit-clearing behavior that marks requested accesses as satisfied across layer positions
- adds one in-memory `insert_rule()` planner that distinguishes the no-match insertion path from matching-rule access extension and merged-layer append behavior without allocating tree nodes or touching object references
- adds one follow-on in-memory tree-search planner around `get_root()`, `walker_node`, and parent or insertion-side selection so the no-match search outcome is reviewable before any `rb_link_node()` or `rb_insert_color()` work is attempted

This slice does not claim rb-tree mutation, object references, rule insertion, hierarchy allocation, merge or inherit behavior, workqueue-backed deferred frees, or any live Landlock hook integration.

The next honest bounded step in this same lane is to add one small in-memory planner for the no-match tree-link branch, limited to `rb_link_node()`, `rb_insert_color()`, and the already-selected insertion site before touching object ownership, hierarchy lifetime, or live policy state.
