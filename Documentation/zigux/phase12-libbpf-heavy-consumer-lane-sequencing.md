# Phase 12 Libbpf Heavy-Consumer Lane Sequencing

This note records the current anti-overlap sequencing for the live Phase 12 `tools/lib/bpf/zigux_segments/` heavy-consumer packet.

It is a coordination artifact, not a closure claim.

## Current posture
- `PHASE12_STATUS=active`
- `PHASE12_SEQUENCE=libbpf-heavy-consumer-anti-overlap`
- shared build-only checker entrypoint: `python3 scripts/zigux/check-build-only-phase12-surface.py`
- focused smoke preflight entrypoint: `make -C zigux phase12-smoke`
- shared build replay entrypoint: `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- Linux-style replay entrypoint: `make -C zigux phase12`
- shipped shared coordination surfaces on `master`: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `tools/lib/bpf/zigux_segments/manifest.json`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`

## Why this note exists

The live Phase 12 libbpf survey is already honest about the current helper-first footing and the still-blocked object-model wall.

What it does not do by itself is stop nearby scheduled runs from collapsing three different kinds of work into one vague `libbpf` bucket:
- shared reviewability upkeep for the shipped Phase 12 packet
- small helper follow-through inside the existing `zigux_segments/` family
- deferred or blocked object-model, loader, bridge, and relocation work

This note turns that risk split into one bounded lane map so future Phase 12 libbpf runs stay inside the smallest real packet that moved.

## Lane map

### 1. Shared reviewability lane: active when the shipped Phase 12 packet drifts
Use this lane only for shared reviewability surfaces that describe or gate the live Phase 12 libbpf packet.

Current shared packet:
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `zigux/tests/phase12_libbpf_manifest.json`
- `zigux/tests/phase12_libbpf_segments.zig`
- `zigux/tests/phase12_libbpf_reviewability.zig`
- `tools/lib/bpf/zigux_segments/manifest.json`
- `zigux/tests/phase12_build.zig`
- `zigux/Makefile`

Do not reopen this lane for:
- direct helper behavior changes inside `tools/lib/bpf/zigux_segments/*.zig`
- object-model or loader scaffolding
- `virtio_net`, `virtio_scsi`, or `nvme` follow-through that merely shares the Phase 12 build

### 2. Ready-next helper lane: bounded helper-first follow-through only
Use this lane only for the two helper-sized follow-ups that the current Phase 12 survey already marks as `ready_next`.

Current ready-next packet:
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` for fdinfo map-info parsing
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` for reused-map compatibility checks
- the paired survey and manifest wording that records those two helper-sized promotions truthfully

Do not widen this lane into:
- direct procfs reads
- bpffs reopen flow
- token creation
- close-on-replacement side effects
- object-model or relocation work

The next honest reopen here is one of those two helper packets becoming landed evidence, not a broad bridge rewrite.

### 3. Deferred bridge and queue-routing lane: keep parked until repo reality changes
Use this lane only if the heavier shared bridge or perf-buffer queue-routing packet itself becomes the explicitly assigned target.

Current deferred packet:
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` for the real file-path and handle bridge
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` for online-CPU routing follow-through

Keep this lane separate because it crosses riskier behavior that the current helper-first packet still does not claim:
- descriptor ownership
- reopen and replacement flow
- token creation
- `perf_event_open` setup
- per-CPU routing and queueing pressure

Do not smuggle this work through the shared reviewability lane or the ready-next helper lane.

### 4. Object-model wall lane: blocked until the missing model surfaces exist
Use this lane only if the assigned task is explicitly about the blocked post-helper wall.

Current blocked packet:
- `tools/lib/bpf/zigux_segments/skeleton.zig`
- `tools/lib/bpf/zigux_segments/object_loader.zig`
- `tools/lib/bpf/zigux_segments/relocation.zig`

These remain separate because they depend on product surfaces that current `master` still does not ship:
- `bpf_object` model parity
- `bpf_program` and `bpf_map` ownership rules
- loader setup
- relocation and verifier-facing behavior

Do not reopen this lane just because the helper-first packet is already dense.

### 5. Shared summary lane: wording-only follow-through for the Phase 12 packet
Use this lane only when the shared wording surfaces drift away from the live Phase 12 libbpf ownership split.

Allowed surfaces:
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Do not use this lane to land helper code, manifest churn, or new test logic.

## Sequencing rule
1. Re-read the shared Phase 12 libbpf survey and reviewability packet first.
2. If the drift is only wording or ownership scope, stay in the shared reviewability or shared summary lane.
3. If the next real code move is one of the two recorded `ready_next` helpers, keep it helper-sized.
4. Keep the deferred bridge and queue-routing packet separate from those helper-sized promotions.
5. Keep the object-model wall separate from every smaller bridge or reviewability step.
6. Do not use this libbpf lane to absorb unrelated Phase 12 driver follow-through just because the shared build is already wired.

## Current anti-overlap correction

Today the strongest Phase 12 libbpf sequencing correction is simple:
- shared reviewability owns the survey, manifest, reviewability gate, and shared build alignment for the current libbpf packet
- the two helper-sized `ready_next` promotions stay smaller than the deferred bridge and queue-routing bucket
- the deferred bridge and queue-routing bucket stays smaller than the blocked object-model, loader, and relocation wall
- wording-only shared-summary repairs stay separate from helper logic and from the other Phase 12 driver lanes

That split matches the live survey packet and keeps future scheduled runs from turning one honest heavy-consumer tranche into overlapping docs, helper, and object-model churn.

## Next bounded step

Leave this note parked unless one of three things happens:
- a shared Phase 12 summary drifts away from this ownership split
- one of the two `ready_next` helper packets becomes the next explicit libbpf task
- the repo lands a real object-model foothold that changes the blocked wall itself

Until then, the safest same-family follow-through is drift control inside the shipped Phase 12 libbpf reviewability packet, not another broad survey rewrite or a speculative bridge expansion.