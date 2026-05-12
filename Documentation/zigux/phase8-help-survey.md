# Phase 8 Help Survey

This survey compares the current `tools/lib/subcmd/help.zig` packet against the Phase 8 tooling-expansion roadmap anchor at `tools/lib/subcmd/help.c`.

## Roadmap asks

- serious repo-hosted tooling rather than tiny helper-only proofs
- helper-first expansion under `tools/lib/subcmd/*.zig`
- output-stable tooling behavior

## Current landed packet

- `tools/lib/subcmd/help.zig` currently owns copied command-name storage, sorting, de-duplication, exclusion, executable-entry filtering, raw `PATH` splitting, injected command-source loading, terminal-dimension parsing and fallback resolution, plus pure pretty-print and section rendering helpers
- the live review packet already includes `Documentation/zigux/phase8-help-slice.md`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, the shared `zigux/tests/phase8_build.zig` route, and the `make -C zigux phase8-help-test` plus `make -C zigux phase8-help-kallsyms-test` entry points listed from the docs root
- the current bounded tests keep the packet on stable helper surfaces: command-list ownership and filtering, injected source loading, raw `PATH` segmentation, terminal sizing, and deterministic output formatting

## Gap vs roadmap

- the current packet already satisfies the roadmap's helper-first and output-stable tooling requirements on a real repo-hosted tooling surface under `tools/lib/subcmd/*.zig`
- the remaining Phase 8 gap is intentional: current `master` still stops short of direct directory walking, live `PATH` or environment reads, direct terminal `ioctl()` probing, and the broader `cmd_help()` control flow owned by `help.c`
- the current `help.zig` tests keep that boundary explicit by preserving raw split evidence while also refusing to treat empty `PATH` segments as implicit cwd command sources

## Next bounded step

Park this survey lane unless a fresh repo reread finds drift between `tools/lib/subcmd/help.zig`, `Documentation/zigux/phase8-help-slice.md`, and `zigux/tests/phase8_help.zig`.

If the lane reopens for substantive roadmap closure, keep the next step to exactly one adapter layer: injected directory-walk parity, injected environment-read parity, or injected terminal-size bridge. Re-run the focused Phase 8 help routes before widening further.
