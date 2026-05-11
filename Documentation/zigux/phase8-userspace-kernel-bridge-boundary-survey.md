# Phase 8 Userspace-Kernel Bridge Boundary Survey

## Status
- `PHASE8_USERSPACE_KERNEL_BRIDGE_STATUS=parked_gap_packet_landed`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P8-L02`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_ROADMAP_PHASE=Phase 8`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_SCOPE=runtime-command-and-environment-plumbing`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_C_ANCHORS=tools/lib/subcmd/exec-cmd.c;tools/lib/subcmd/help.c`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_SHARED_NOTE=Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_VALIDATION_ENTRYPOINT=python3 scripts/zigux/validate-phase8.py`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_LINUX_STYLE_VALIDATION=make -C zigux phase8-validate`

## Purpose

This parked Phase 8 gap note keeps the roadmap-backed command and environment
control surface reviewable without pretending that the current Zigux packet has
closed direct process-launch, live environment-read, or terminal-probing parity.

The note is intentionally narrow:
- keep the roadmap anchors explicit
- keep the parked current-tree command and help packet explicit
- keep the shared Phase 8 lane note and validation entrypoint explicit
- keep the next bounded follow-through step explicit until later Phase 8 work lands
  a smaller truthfulness or replay update inside the same command packet

## Current Measurable Status

Current public default-branch tree readback shows the parked command and help
packet still exposes:
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-help-slice.md`
- `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_help.zig`
- `zigux/tests/phase8_help_only_build.zig`

The bounded evidence packet for that parked command surface remains:
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `python3 scripts/zigux/validate-phase8.py`
- `make -C zigux phase8-validate`

Authenticated contents reads for some Phase 8 files are inconsistent from this
environment, so current public default-branch tree evidence and readable blob
content should win over older absent-file assumptions.

That packet keeps the roadmap-backed command and environment plumbing gap explicit
without claiming direct `execvp()` parity, direct process-launch ownership, live
OS environment reads, or direct terminal probing on current `master`.

## Roadmap Gap

The product roadmap still names Phase 8 as the first tooling-expansion tranche for:
- `tools/lib/subcmd/exec-cmd.c`
- `tools/lib/subcmd/help.c`

Current `master` now preserves parked command-lane and help-lane review surfaces
around this area, but the same packet still stops short of full process-launch,
environment-plumbing, and terminal-probing parity. This note should therefore
remain the truthful bridge between the roadmap target and the bounded current-tree
evidence rather than reverting to older missing-file wording.

## Next Bounded Step

If a later Phase 8 lane changes any of the parked command-lane or help-lane files,
re-read this note together with `Documentation/zigux/phase8-tooling-lane-sequencing.md`,
`python3 scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, `scripts/zigux/README.md`,
`zigux/Makefile`, and the current Phase 8 test tree before widening broader Phase 8 summaries.
Until then, keep this survey parked and keep follow-up inside one bounded command-packet
truthfulness or replay step rather than rebuilding the older missing-control-surface claim.
