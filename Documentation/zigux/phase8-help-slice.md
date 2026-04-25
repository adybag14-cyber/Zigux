# Phase 8 Help Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/help.c`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=help-command-list-starter`
- scope: owned command-list handling, injected executable-entry filtering, and print-layout planning only
- product boundary:
  - `tools/lib/subcmd/help.zig`
  - `zigux/tests/phase8_help.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/subcmd/help.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/subcmd/*.zig` as the first Zigux destination for this tranche.

This lane keeps the shipped `help.zig` starter slice aligned with the stable command-list manipulation logic from `help.c`, because that surface is still easier to validate honestly than terminal-size probing, directory walking, environment inspection, or output emission.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/subcmd/help.zig`

2. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig`

3. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current starter slice covers:

- owned `add_cmdname()`-style command-name storage with explicit copy semantics
- `cmdname_compare()`-adjacent lexical sorting
- `uniq()` behavior for adjacent duplicates after sorting
- `exclude_cmds()` behavior for sorted exclusion lists
- `is_in_cmdlist()` membership checks
- injected command-entry filtering that strips the `perf-` prefix and optional `.exe` suffix before storage
- `pretty_print_string_list()`-adjacent column and row planning without direct terminal I/O

The current tests check:

- copied command names do not alias mutable caller buffers
- sorted duplicate removal keeps one stable owned copy
- sorted exclusions remove matching entries without disturbing survivors
- executable-entry filtering ignores non-prefixed, non-executable, and prefix-only candidates while stripping `.exe` suffixes
- membership and longest-name tracking stay aligned with stored entries
- layout planning preserves the same column math used before printing, including the single-column fallback for narrow terminals and the empty-list row contract

## Non-goals

This slice does not yet claim:

- `opendir()` or `readdir()` parity for command discovery
- terminal-size discovery through environment variables or `ioctl()`
- direct `printf()` output formatting or PATH scanning behavior

## Next bounded step

Stay in `tools/lib/subcmd/help.zig` and add an injected command-source layer that batches directory-entry iteration for `load_command_list()` parity, or add an injected terminal-size surface before attempting any direct output-emission parity.
