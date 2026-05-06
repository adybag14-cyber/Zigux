# Phase 13 Landlock Ruleset Ownership Note

- `PHASE13_STATUS=active`
- `PHASE13_LANE_KEY=P13-Y03`
- `PHASE13_SCOPE=security/landlock/ruleset.zig helper-local ownership and fixture governance`

This note closes one narrow reviewability gap around `security/landlock/ruleset.zig`: the helper already had slice and survey notes, but it did not yet have a dedicated ownership note that says what this helper packet owns, what nearby Landlock lanes own instead, and which review artifacts must move together when this helper changes.

## Helper-owned surface

`security/landlock/ruleset.zig` owns only in-memory planning around these helper-local branches from `security/landlock/ruleset.c`:

- `landlock_create_ruleset()` empty-ruleset rejection and one-layer initialization planning
- handled-access unioning across filesystem, network, and scope masks
- `landlock_init_layer_masks()` per-layer handled-access planning
- `landlock_unmask_layers()` bit-clearing reviewability
- `insert_rule()` matching-rule access extension versus merged-layer append planning
- tree-search outcome planning around `get_root()` and `walker_node`
- no-match tree-link mode planning around `rb_link_node()` and `rb_insert_color()`

## Not owned here

This helper note does not authorize widening into:

- `security/landlock/syscalls.zig` file-descriptor, path, or `landlock_restrict_self()` behavior
- `rb_replace_node()`, live rb-tree storage, object ownership, hierarchy lifetime, or deferred free behavior
- real Landlock policy enforcement, hook integration, or live LSM state

Those surfaces stay outside this helper packet until a separately justified lane carries matching helper, test, manifest, and survey evidence.

## Fixture governance

Any helper-local change to `security/landlock/ruleset.zig` must keep these artifacts aligned in the same bounded review packet:

- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`

No lane should flip the live-tree blocker or broaden the helper-owned surface unless the helper behavior, the dedicated gate, the packet checker, and the survey wording all move together.

## Next bounded step

Leave this note parked unless future `ruleset.zig` work creates drift between helper ownership, the live-tree blocker, and the five review artifacts above.