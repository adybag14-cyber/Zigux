# Phase 8 Help Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/help.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=help-command-source-and-terminal-starter`
- scope: owned command-list handling, injected command-source filtering, injected raw-`PATH` splitting, injected terminal-dimensions resolution, and pure pretty-print emission planning
- maintenance note: the current slice now also includes pure section-level `list_commands()` formatting with injected title and exec-path inputs, while still avoiding direct environment, directory, and terminal side effects
- product boundary:
  - `tools/lib/subcmd/help.zig`
  - `zigux/tests/phase8_help.zig`
  - `zigux/tests/phase8_help_only_build.zig`
  - `zigux/tests/phase8_help_kallsyms_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/subcmd/help.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/subcmd/*.zig` as the first Zigux destination for this tranche.

This lane keeps the shipped `help.zig` parked slice aligned with the stable command-list manipulation logic from `help.c`, because that surface is still easier to validate honestly than direct terminal-size probing, directory walking, or environment inspection. Pure writer-driven output emission remains in scope here because it is driven entirely by injected inputs and stays reviewable without widening into terminal, environment, or CLI side effects.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/subcmd/help.zig`

2. run the focused Phase 8 help replay
- `zig build test --build-file zigux/tests/phase8_help_only_build.zig --summary all`

3. run the focused shared help and symbol gate
- `zig build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all`

4. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

5. run the convenience targets
- `make -C zigux phase8-help-test`
- `make -C zigux phase8`

## Current parity surface

The current parked slice covers:

- owned `add_cmdname()`-style command-name storage with explicit copy semantics
- owned command-name and raw-`PATH` entry storage that now also frees temporary copied slices cleanly if allocator growth fails before the new entry is retained
- `cmdname_compare()`-adjacent lexical sorting
- `uniq()` behavior for adjacent duplicates after sorting
- `exclude_cmds()` behavior for sorted exclusion lists
- `is_in_cmdlist()` membership checks
- injected command-entry filtering that strips the `perf-` prefix and optional `.exe` suffix before storage
- injected command-source loading that models `load_command_list()` exec-path priority, PATH de-duplication, and cross-list exclusion without direct `readdir()` or `stat()` calls
- injected command-source loading also re-normalizes any caller-seeded main command list before PATH-side exclusion, so upstream precomputed exec-path entries stay on the same sort, uniq, and de-duplication path as direct discovery
- raw `PATH` string splitting that preserves empty colon-delimited segments, including a fully empty `PATH` string, before reusing the same prefix-aware command-source loader, keeping the env-`PATH` helper on the exact same sort, uniq, and exclusion path as the shared source helper
- injected `get_term_dimensions()`-adjacent resolution that prefers explicit `LINES` and `COLUMNS` values before fallback terminal dimensions or the default `25x80`
- `pretty_print_string_list()`-adjacent column and row planning without direct terminal I/O
- `pretty_print_string_list()`-adjacent pure output emission through an injected writer, including the same column-major traversal, two-space indent, and ragged-last-column padding rules as the C helper
- `list_commands()`-adjacent shared longest-name calculation plus pure section-level rendering for the exec-path and PATH headings, underline widths, blank-line separation, and empty-section suppression without direct `getenv()` or `get_argv_exec_path()` reads

The current tests check:

- copied command names do not alias mutable caller buffers
- owned command-name and raw-`PATH` entry helpers release temporary copied slices cleanly when allocator failure interrupts append growth
- sorted duplicate removal keeps one stable owned copy
- sorted exclusions remove matching entries without disturbing survivors
- executable-entry filtering ignores non-prefixed, non-executable, and prefix-only candidates while stripping `.exe` suffixes
- command-source loading keeps the exec-path list stable, skips the exec-path directory when it also appears on PATH, removes commands already present in the exec-path list, and preserves the `perf-` default prefix behavior
- command-source loading keeps caller-seeded main command lists sorted and de-duplicated before PATH-side exclusion, preventing already-known commands from leaking back in when exec-path discovery is unavailable or precomputed upstream
- raw `PATH` splitting keeps a fully empty string plus leading, repeated, and trailing empty segments explicit so later injected population can follow the same branch shape as `help.c`, and the env-`PATH` wrapper keeps custom-prefix filtering on the same shared helper path as the direct source loader
- helper-local `tools/lib/subcmd/help.zig` tests own the fully empty `PATH` fallback and PATH-only fallback edges directly, so the phase replay stays centered on integrated command discovery and section rendering instead of replaying those helper-local cases again
- terminal-dimensions resolution only accepts non-zero `LINES` plus `COLUMNS` pairs, otherwise falls back to injected terminal sizes or the `25x80` default
- membership and longest-name tracking stay aligned with stored entries
- layout planning preserves the same column math used before printing, including the single-column fallback for narrow terminals, the empty-list row contract, and environment-driven column selection through the injected terminal helper
- pretty-print output stays testable without `printf()` by reusing the injected terminal-dimensions path and emitting the same row text the C helper would print
- section-level output stays testable without `printf()` by rendering the same `available <title> in '<path>'` and `$PATH` headings, underline lengths, shared column width, section spacing, and empty-section suppression that `list_commands()` uses in `help.c`
- the parked help packet also stays reviewable through the shared `zigux/tests/phase8_help_kallsyms_only_build.zig` replay, so the combined help-plus-symbol tranche does not need the full Phase 8 bundle just to prove the existing `help` surface still wires cleanly beside `kallsyms`

## Non-goals

This slice does not yet claim:

- `opendir()` or `readdir()` parity for command discovery
- direct `ioctl()`-backed terminal probing
- direct environment reads or a full `cmd_help()`-adjacent CLI surface

## Next bounded step

The current bounded gap versus the broader Phase 8 tooling packet is now the replay shape rather than missing helper behavior: `help.zig` can be reviewed through its own `phase8_help_only_build.zig` shard, the shared `phase8_help_kallsyms_only_build.zig` replay, and the shared `phase8_build.zig` tooling replay without hiding only inside the full tooling bundle. Park this lane unless a fresh helper-only parity gap appears; the next honest follow-up should only reopen it for another exact formatting or command-source parity edge rather than widening into direct environment reads, directory walking, or full CLI behavior.
