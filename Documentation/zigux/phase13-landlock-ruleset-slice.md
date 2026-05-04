# Phase 13 Landlock Ruleset Slice

This bounded Phase 13 slice keeps `security/landlock/ruleset.zig` as a pure helper-first lab anchored to `security/landlock/ruleset.c`.

The current helper lab stays intentionally narrow:

- models the empty-ruleset rejection and single-layer initialization path of `landlock_create_ruleset()` without claiming allocation, mutex setup, refcounts, or anonymous-fd plumbing
- unions filesystem, network, and scope access masks across a layer stack so the lane can describe the handled-access summary that later ruleset and domain checks rely on
- mirrors the per-layer request initialization done by `landlock_init_layer_masks()`, including the always-denied-by-default filesystem access bit when any filesystem mask is active
- captures the `landlock_unmask_layers()` bit-clearing behavior and rejects duplicate or out-of-order layer shapes so the helper lab enforces the same ordered-layer invariant before any live ruleset state exists
- records the small `build_check_rule()`, `build_check_layer()`, and `build_check_ruleset()` storage-capacity invariants as helper-visible data so the lane keeps its layer, rule-count, and access-field representation bounds explicit
- adds one in-memory `insert_rule()` planner that distinguishes the no-match insertion path from matching-rule access extension and merged-layer append behavior without allocating tree nodes or touching object references
- adds one follow-on in-memory tree-search planner around `get_root()`, `walker_node`, and parent or insertion-side selection so the no-match search outcome is reviewable before any `rb_link_node()` or `rb_insert_color()` work is attempted
- adds one tiny tree-link planner for the no-match branch so the `rb_link_node()` and `rb_insert_color()` handoff is reviewable as an explicit root or left or right link mode before any live rb-tree mutation or object ownership is claimed
- adds one bounded `landlock_find_rule()` lookup planner so root selection, `root->rb_node` descent, and match-versus-null outcomes stay reviewable as data before any live rb-tree lookup parity is implied
- adds one bounded `create_rule()` materialization planner so copied layer stacks, optional merged-layer append behavior, canonical layer-shape validation, `RB_CLEAR_NODE()` initialization, and key-type-owned object-reference intent are reviewable as data without claiming allocation or live ownership transfer
- adds one bounded helper-only replacement planner so matched-rule updates around `rb_replace_node()`, previous-rule release intent, and inode-only previous-object release intent are reviewable as data before any actual rb-tree mutation or ownership handoff is claimed
- adds one bounded `free_rule()` release planner so the unconditional `might_sleep()` boundary, null-rule early return, inode-only `landlock_put_object()` intent, and present-rule `kfree()` intent are reviewable as data without mutating live refcounts or deferred work state

This slice does not claim rb-tree mutation, object references, rule insertion, hierarchy allocation, merge or inherit behavior, workqueue-backed deferred frees, or any live Landlock hook integration.

The next honest bounded step in this same lane is blocked until there is a justified way to study actual `rb_replace_node()` mutation, live object ownership transfer, hierarchy lifetime, workqueue-backed teardown, and other live ruleset state without pretending this helper lab already owns real Landlock storage or policy enforcement.