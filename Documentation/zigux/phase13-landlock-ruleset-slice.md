# Phase 13 Landlock Ruleset Slice

This bounded Phase 13 slice keeps `security/landlock/ruleset.zig` as a pure helper-first lab anchored to `security/landlock/ruleset.c`.

The current helper lab stays intentionally narrow:

- models the empty-ruleset rejection and single-layer initialization path of `landlock_create_ruleset()` without claiming allocation, mutex setup, refcounts, or anonymous-fd plumbing
- unions filesystem, network, and scope access masks across a layer stack so the lane can describe the handled-access summary that later ruleset and domain checks rely on
- mirrors the per-layer request initialization done by `landlock_init_layer_masks()`, including the always-denied-by-default filesystem access bit when any filesystem mask is active
- captures the `landlock_unmask_layers()` bit-clearing behavior that marks requested accesses as satisfied across layer positions
- adds one in-memory `insert_rule()` planner that distinguishes the no-match insertion path from matching-rule access extension and merged-layer append behavior without allocating tree nodes or touching object references
- adds one follow-on in-memory tree-search planner around `get_root()`, `walker_node`, and parent or insertion-side selection so the no-match search outcome is reviewable before any `rb_link_node()` or `rb_insert_color()` work is attempted
- adds one tiny tree-link planner for the no-match branch so the `rb_link_node()` and `rb_insert_color()` handoff is reviewable as an explicit root or left or right link mode before any live rb-tree mutation or object ownership is claimed

The dedicated ownership note in `Documentation/zigux/phase13-landlock-ruleset-ownership.md` keeps the helper boundary explicit and requires the slice note, survey note, manifest, and test gate to move together whenever this helper packet changes.

This slice does not claim rb-tree mutation, object references, rule insertion, hierarchy allocation, merge or inherit behavior, workqueue-backed deferred frees, or any live Landlock hook integration.

The next honest bounded step in this same lane is blocked until there is a justified way to study `rb_replace_node()`, object ownership, hierarchy lifetime, and other live ruleset state without pretending this helper lab already owns real Landlock storage or policy enforcement.