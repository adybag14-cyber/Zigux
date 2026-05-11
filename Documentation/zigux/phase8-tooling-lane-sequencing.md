# Phase 8 Tooling Lane Sequencing

This note records the current anti-overlap owner map for the live Phase 8 userspace-adjacent tooling packet.

It is a coordination artifact, not a closure claim.

## Current posture
- `PHASE8_STATUS=parked`
- `PHASE8_SEQUENCE=tooling-lane-anti-overlap`
- shared validator-first entrypoint: `python3 scripts/zigux/validate-phase8.py`
- shared make validation route: `make -C zigux phase8-validate`
- shared docs and reminder surfaces still present on current `master`: `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- current repo-reality caution: the default-branch tree read surface no longer exposes the older `Documentation/zigux/phase8-*-slice.md`, `tools/lib/subcmd/`, `tools/lib/symbol/`, `tools/lib/bpf/zigux_segments/`, or `zigux/tests/phase8_*` packet that some shared summaries still name
- freeze-map posture: this lane stays in repo-hosted tooling review surfaces only and does not reopen any deep-core freeze anchor

## Lane map

### 1. Command lane
Use this lane only if current `master` again ships concrete `tools/lib/subcmd/` Phase 8 anchors.

Current repo reality:
- the default-branch tree read surface does not currently expose `tools/lib/subcmd/`
- the default-branch tree read surface does not currently expose the older `zigux/tests/phase8_exec_cmd*.zig` or `zigux/tests/phase8_help*.zig` companions
- treat lingering command-lane references in shared summaries as stale wording, not live packet evidence

Do not reopen this lane until the tree again carries explicit command-lane files on `master`.

### 2. Symbol lane
Use this lane only if current `master` again ships concrete `tools/lib/symbol/` Phase 8 anchors.

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
- current `master` still carries only the shared reminder packet and this owner-map note for Phase 8 on the default-branch read surface
- treat missing slice-note, tests-root shard, and tool-tree filenames as removed or absent until the tree itself shows them again
- when this lane reopens, use the default-branch tree plus the shared docs, validator, Makefile, and workflow surfaces as the first-pass truth sources

## Sequencing rule
1. Re-read the shared packet surfaces first.
2. Confirm repo reality through the default-branch tree or exact file readback before trusting older Phase 8 inventories.
3. Keep follow-up inside the shared wording lane unless concrete command, symbol, or libbpf files reappear on `master`.
4. Prefer the next one-file or tightly coupled same-lane truthfulness repair over broader Phase 8 expansion.
5. Validate through exact default-branch readback before treating the packet as parked again.

## Next bounded step
The next honest reopen cue is the docs-root Phase 8 summary in `Documentation/zigux/README.md`: it still names removed slice-note files and tree-backed packet members instead of the current shared reminder surfaces and this owner-map note.
