# Phase 8 Userspace-Kernel Bridge Boundary Survey

## Status
- `PHASE8_USERSPACE_KERNEL_BRIDGE_STATUS=parked_gap_packet_landed`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P6-L13`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_ROADMAP_PHASE=Phase 8`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_SCOPE=runtime-command-and-environment-plumbing`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_C_ANCHORS=tools/lib/subcmd/exec-cmd.c;tools/lib/subcmd/help.c`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_SHARED_NOTE=Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_VALIDATION_ENTRYPOINT=python3 scripts/zigux/validate-phase8.py`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_LINUX_STYLE_VALIDATION=make -C zigux phase8-validate`

## Purpose

This parked Phase 8 gap note keeps the roadmap-backed command and environment
control surface reviewable without pretending that the direct Zigux packet already
ships on current `master`.

The note is intentionally narrow:
- keep the roadmap anchors explicit
- keep the missing current-tree command and help packet explicit
- keep the shared Phase 8 lane note and validation entrypoint explicit
- keep the next bounded follow-through step explicit until later Phase 8 work lands
  concrete tool-tree or test-tree anchors

## Current Measurable Status

Current `master` does not currently expose:
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-help-slice.md`
- `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_help.zig`
- `zigux/tests/phase8_help_only_build.zig`

The bounded evidence packet instead remains:
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `python3 scripts/zigux/validate-phase8.py`
- `make -C zigux phase8-validate`

That packet keeps the roadmap-backed command and environment plumbing gap explicit
without claiming direct process-launch parity, live environment reads, terminal
probing, or shipped `tools/lib/subcmd/*.zig` delivery on current `master`.

## Roadmap Gap

The product roadmap still names Phase 8 as the first tooling-expansion tranche for:
- `tools/lib/subcmd/exec-cmd.c`
- `tools/lib/subcmd/help.c`

Current `master` only preserves the shared Phase 8 review surfaces around this area.
Until concrete command-lane files return to the tree, this note should remain the
truthful bridge between the roadmap target and the current default-branch evidence.

## Next Bounded Step

If a later Phase 8 lane lands any of the missing command-lane or help-lane files,
update this note together with `Documentation/zigux/phase8-tooling-lane-sequencing.md`
before widening broader Phase 8 summaries. Until then, keep this survey parked and
keep follow-up inside the missing control-surface note rather than rebuilding the
older command packet by implication alone.
