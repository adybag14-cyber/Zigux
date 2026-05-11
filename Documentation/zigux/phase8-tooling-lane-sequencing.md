# Phase 8 Tooling Lane Sequencing

This note records the current anti-overlap owner map for the live Phase 8 userspace-adjacent tooling packet.

It is a coordination artifact, not a closure claim.

## Current posture
- `PHASE8_STATUS=parked`
- `PHASE8_SEQUENCE=tooling-lane-anti-overlap`
- shared validator-first entrypoint: `python3 scripts/zigux/validate-phase8.py`
- shared make validation route: `make -C zigux phase8-validate`
- shared docs and reminder surfaces still present on current `master`: `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- command-gap companion: `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- current repo-reality caution: the default-branch tree read surface no longer exposes the older `Documentation/zigux/phase8-*-slice.md`, `tools/lib/subcmd/`, `tools/lib/symbol/`, `tools/lib/bpf/zigux_segments/`, or `zigux/tests/phase8_*` packet that some shared summaries still name
- current shared-surface drift: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `zigux/Makefile` still name removed Phase 8 slice-note files, shard tests, or libbpf-segment members even though the default-branch tree read surface no longer exposes those packet anchors
- freeze-map posture: this lane stays in repo-hosted tooling review surfaces only and does not reopen any deep-core freeze anchor

## Lane map

### 1. Command lane
Use this lane only for roadmap-backed command and environment control-surface gap work until current `master` again ships concrete `tools/lib/subcmd/` anchors.

Current repo reality:
- the default-branch tree read surface does not currently expose `Documentation/zigux/phase8-exec-cmd-slice.md` or `Documentation/zigux/phase8-help-slice.md`
- the default-branch tree read surface does not currently expose `tools/lib/subcmd/exec-cmd.zig` or `tools/lib/subcmd/help.zig`
- the default-branch tree read surface does not currently expose the older `zigux/tests/phase8_exec_cmd*.zig` or `zigux/tests/phase8_help*.zig` companions
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` is the dedicated parked review note for this roadmap-versus-tree gap
- treat lingering command-lane references in shared summaries as stale wording, not live packet evidence

Keep follow-up inside that gap note plus this owner-map note until the tree again carries explicit command-lane files on `master`.

### 2. Symbol lane
Use this lane only if current `master` again ships concrete `tools/lib/symbol/` anchors.

Current repo reality:
- the default-branch tree read surface does not currently expose `tools/lib/symbol/`
- the default-branch tree read surface does not currently expose the older `zigux/tests/phase8_kallsyms*.zig` companions
- treat lingering symbol-lane references in shared summaries as stale wording, not live packet evidence

Do not reopen this lane until the tree again carries explicit symbol-lane files on `master`.

### 3. Libbpf helper lane
Use this lane only if current `master` again ships concrete `tools/lib/bpf/zigux_segments/` anchors or their paired focused Phase 8 shard tests.

Current repo reality:
- the default-branch tree read surface does not currently expose `tools/lib/bpf/zigux_segments/`
- the default-branch tree read surface does not currently expose the older `zigux/tests/phase8_*` libbpf shard packet
- treat lingering libbpf-lane references in shared summaries as stale wording, not live packet evidence

Do not reopen this lane until the tree again carries explicit libbpf helper files or shard tests on `master`.

### 4. Shared wording lane
Use this lane for bounded truthfulness work across the shared Phase 8 reminder surfaces when repo reality drifts.

Allowed surfaces:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Current wording-lane caution:
- current `master` still carries only the shared reminder packet, this owner-map note, and the dedicated command-gap survey for Phase 8 on the default-branch read surface
- the shared reminder packet still overstates removed slice-note, shard-test, and libbpf-segment members on several reminder surfaces
- treat missing slice-note, tests-root shard, and tool-tree filenames as removed or absent until the tree itself shows them again
- when this lane reopens, use the default-branch tree plus the shared docs, validator, Makefile, workflow, and the dedicated command-gap survey as the first-pass truth sources

## Sequencing rule
1. Re-read the shared packet surfaces first.
2. Confirm repo reality through the default-branch tree or exact file readback before trusting older Phase 8 inventories.
3. Keep follow-up inside the command-gap note when the command or help packet is still absent, or inside the shared wording lane unless concrete command, symbol, or libbpf files reappear on `master`.
4. Prefer the next one-file or tightly coupled same-lane truthfulness repair over broader Phase 8 expansion.
5. Validate through exact default-branch readback before treating the packet as parked again.

## Next bounded step
The next honest reopen cue still starts at the docs-root Phase 8 summary in `Documentation/zigux/README.md`, then continues through `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `zigux/Makefile`: those shared reminder surfaces still name removed slice-note files, shard tests, and libbpf-segment members instead of the current shared reminder packet, this owner-map note, and the dedicated command-gap survey.
