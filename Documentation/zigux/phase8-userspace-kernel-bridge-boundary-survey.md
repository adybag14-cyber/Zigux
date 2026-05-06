# Phase 8 Userspace-Kernel Bridge Boundary Survey

This document records the bounded Phase 8 userspace-adjacent tooling boundary around the current libbpf bridge helpers parked under `tools/lib/bpf/zigux_segments/`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=userspace-kernel-bridge-boundary-survey`
- scope: helper-first review of the current fdinfo bridge packet plus the still-queued adjacent bridge steps only
- product boundary:
  - `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  - `zigux/tests/phase8_file_path_handle_bridge.zig`
  - `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
  - `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
  - `Documentation/zigux/phase8-libbpf-segment-survey.md`

## Why this survey exists

The live Phase 8 packet already carries a bounded fdinfo helper slice, but the adjacent bridge boundary was still only implicit across the file-path helper note and the broader libbpf segment survey. This survey makes that boundary explicit so the validator-first Phase 8 packet can describe the shipped helper and the queued follow-through without implying procfs, bpffs, or object-model closure.

## Current landed packet

The currently landed bridge-side helper remains intentionally small:

- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` keeps exact `"/proc/%d/fdinfo/%d"` assembly and bounded fdinfo map-info parsing reviewable
- `zigux/tests/phase8_file_path_handle_bridge.zig` keeps the helper packet wired to stable path, parsing, and summary expectations
- the helper stays smaller than direct procfs reads, pinned-object reopen flow, token creation, and descriptor lifecycle behavior

## Boundary findings

The current packet is productively landed, but the remaining bridge-facing work still needs a sharp fence:

- `planTokenPreparation()` remains outside the shipped helper packet because token construction would widen the slice from stable text parsing into capability and ownership setup
- `resolveReusePinnedMapAttempt()` remains queued because map reuse needs explicit path-open, reopen, and compatibility decisions that go beyond the current fdinfo-only helper
- direct procfs reads, bpffs opens, `bpf_obj_get()` reopen flow, and fd close or ownership semantics remain intentionally outside the current packet
- the current helper-first bridge note should stay adjacent to the libbpf segment survey until the queued bridge packet can be reviewed as one tighter step

## Review gates

1. run the shared Phase 8 validator route first
- `make -C zigux phase8-validate`

2. run the shared Phase 8 validator self-test
- `python3 scripts/zigux/validate-phase8.py --self-test`

3. run the shared Phase 8 validator
- `python3 scripts/zigux/validate-phase8.py`

4. run the focused file-path bridge replay
- `zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all`

5. run the shared Phase 8 replay
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
- `make -C zigux phase8`

## Non-goals

This survey does not claim:

- direct procfs file reads
- token materialization or capability handoff
- map reopen or bpffs compatibility closure
- object-model or loader parity
- descriptor duplication, transfer, or close ownership rules

## Next bounded step

Keep this survey parked beside the landed fdinfo helper packet until one adjacent bridge step is ready to move as a single bounded review surface. Keep the shared `make -C zigux phase8-validate` route explicit in that parked boundary so validator-first review stays ahead of the bridge-side replay. The next honest reopen remains the smallest helper-first packet that can connect the current fdinfo note to queued reuse planning without widening into direct procfs reads, bpffs opens, token creation, or loader-facing libbpf work.
