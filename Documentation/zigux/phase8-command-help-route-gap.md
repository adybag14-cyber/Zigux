# Phase 8 Shared Command-Help Route Gap

This note records one bounded shared-survey gap inside the Phase 8 userspace-adjacent tooling packet.

## Status

- `PHASE8_STATUS=parked_shared_route_gap`
- `PHASE8_LANE_KEY=P8-L01`
- phase: `Phase 8`
- roadmap anchors: `tools/lib/subcmd/exec-cmd.c`, `tools/lib/subcmd/help.c`, `tools/lib/symbol/kallsyms.c`, and `tools/lib/bpf/libbpf.c`
- scope: shared command-and-bridge reminder truthfulness only

## Why this note exists

The roadmap keeps `tools/lib/subcmd/*.zig` inside the same Phase 8 userspace-adjacent tooling tranche as the segmented `libbpf` work, but the shared bridge-boundary survey should stay honest about which returned command-surface routes are now directly reviewable on current `master`.

Current repo evidence already exposes a larger parked help-side route packet than the shared bridge survey names directly. That is a shared reminder gap, not a helper-behavior gap.

## Current returned command packet

Current public default-branch readback shows the parked command-and-help packet includes:

- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-help-slice.md`
- `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_help.zig`
- `zigux/tests/phase8_help_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`
- `scripts/zigux/check-phase8-help-kallsyms-packet.py`
- `make -C zigux phase8-help-test`
- `make -C zigux phase8-help-kallsyms-test`
- `make -C zigux phase8-validate`

The same repo packet still keeps `kallsyms` ownership separate from this shared command lane. The shared `phase8_help_kallsyms_only_build.zig` route is validation overlap, not a lane handoff away from the dedicated symbol packet.

## Exact gap vs the shared bridge survey

`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` already keeps the parked command-and-help packet explicit, but it still underdescribes the returned help-side route evidence that now sits beside that packet on current `master`.

The shared survey currently stops at the direct help file and focused help test shard. It does not yet name the returned:

- `zigux/tests/phase8_help_kallsyms_only_build.zig` overlap shard
- `scripts/zigux/check-phase8-help-kallsyms-packet.py` shared checker
- `make -C zigux phase8-help-test` focused help wrapper
- `make -C zigux phase8-help-kallsyms-test` shared overlap wrapper

That omission matters because the roadmap-backed shared Phase 8 reminder should show the currently reviewable command-surface packet without collapsing help and kallsyms ownership together or treating the returned overlap route as missing.

## Non-goals

This note does not reopen:

- `tools/lib/subcmd/help.zig` behavior
- `tools/lib/subcmd/exec-cmd.zig` behavior
- `tools/lib/symbol/kallsyms.zig` parser-local ownership
- `tools/lib/bpf/zigux_segments/*` helper implementation work
- broader validator or Makefile ownership beyond the already returned route names

## Next bounded step

If the shared Phase 8 bridge-boundary survey becomes directly writable through the same exact source path as the rest of this packet, fold this route evidence back into `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` and keep the wording narrow:

- preserve the dedicated `kallsyms` owner lane
- keep `phase8_help_kallsyms_only_build.zig` framed as shared validation overlap only
- keep `make -C zigux phase8-help-test` and `make -C zigux phase8-help-kallsyms-test` explicit as returned command-surface routes
- do not widen into process-launch parity, direct environment reads, terminal probing, or libbpf helper behavior
