# Phase 12 Libbpf Heavy-Consumer Lane Sequencing

This note records the current anti-overlap sequencing for the live Phase 12 `tools/lib/bpf/zigux_segments/` heavy-consumer packet.

It is a coordination artifact, not a closure claim.

## Current posture
- `PHASE12_STATUS=active`
- `PHASE12_SEQUENCE=libbpf-heavy-consumer-anti-overlap`
- direct smoke preflight entrypoint: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
- shared build-only checker entrypoints: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py`
- focused smoke preflight entrypoint: `make -C zigux phase12-smoke`
- shared build replay entrypoint: `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- Linux-style replay entrypoint: `make -C zigux phase12`
- when `zig` is unavailable on `PATH`, keep the shipped Make routes explicit as `make -C zigux phase12-smoke ZIG=<attached-zig-path>` and `make -C zigux phase12 ZIG=<attached-zig-path>` rather than implying a validator-first, helper-local, or libbpf-only replay surface; keep the shared build-only checker reruns explicit before or beside those attached-toolchain Make reruns so reviewability drift still fails closed on the same shared packet
- shipped shared coordination surfaces on `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_libbpf_snapshot_determinism.zig`, `tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/verify.zig`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`

## Why this note exists

The live Phase 12 libbpf survey is already honest about the current helper-first footing and the still-blocked object-model wall.

What it does not do by itself is stop nearby scheduled runs from collapsing four different kinds of work into one vague `libbpf` bucket:
- shared reviewability upkeep for the shipped Phase 12 packet, including the dedicated `zigux_segments/verify.zig` shard beneath the broader survey and replay gates
- tracked pure-helper upkeep for the five deterministic helper paths already carried by the Phase 12 snapshot fixtures
- landed bridge-local helper-foundation upkeep inside the existing `zigux_segments/` family
- deferred or blocked object-model, loader, bridge, and relocation work

This note turns that risk split into one bounded lane map so future Phase 12 libbpf runs stay inside the smallest real packet that moved.

## Lane map

### 1. Shared reviewability lane: active when the shipped Phase 12 packet drifts
Use this lane only for shared reviewability surfaces that describe or gate the live Phase 12 libbpf packet.

Current shared packet:
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `zigux/tests/phase12_libbpf_manifest.json`
- `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
- `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`
- `zigux/tests/phase12_libbpf_segments.zig`
- `zigux/tests/phase12_libbpf_reviewability.zig`
- `zigux/tests/phase12_libbpf_snapshot_determinism.zig`
- `tools/lib/bpf/zigux_segments/manifest.json`
- `tools/lib/bpf/zigux_segments/verify.zig`
- `scripts/zigux/check-build-only-phase12-surface.py`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/phase12_build.zig`
- `zigux/Makefile`

The direct PMO drift-control reruns inside that shared packet are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py` before or beside the workflow-backed replay. That same shared packet should also keep `tools/lib/bpf/zigux_segments/verify.zig` explicit as the focused compile-and-entrypoint shard beneath the broader reviewability and build replays.

Do not reopen this lane for:
- direct helper behavior changes inside `tools/lib/bpf/zigux_segments/*.zig`
- object-model or loader scaffolding
- `virtio_net`, `virtio_scsi`, or `nvme` follow-through that merely shares the Phase 12 build

### 2. Tracked pure-helper lane: keep the deterministic five-path helper packet explicit
Use this lane only when the shared wording, snapshot fixtures, or deterministic replay need to keep the pure helper packet separate from the bridge-local foundations and the heavier deferred buckets.

`PHASE12_LIBBPF_TRACKED_HELPER_COUNT=5`

Current tracked pure-helper packet:
- `tools/lib/bpf/zigux_segments/type_names.zig`
- `tools/lib/bpf/zigux_segments/cpu_mask.zig`
- `tools/lib/bpf/zigux_segments/logging.zig`
- `tools/lib/bpf/zigux_segments/pin_path.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `zigux/tests/fixtures/phase12_libbpf_snapshot.json`
- `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`
- `zigux/tests/phase12_libbpf_snapshot_determinism.zig`

This packet is already landed on current `master` and is intentionally smaller than the bridge-local helper packet: the ordered-path snapshot fixture and deterministic snapshot-digest evidence exact-track the five pure helper files without blurring them into `file_path_handle_bridge.zig`, the deferred bridge bucket, or the blocked object-model wall.

Do not widen this lane into:
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- direct procfs reads
- token creation
- queue-routing work
- object-model or relocation work

The next honest reopen here is drift control around the exact five-path helper packet, not treating the tracked helper set as if it were the same boundary as the bridge-local helper foundations.

### 3. Landed helper-foundation lane: keep the smaller bridge-local footholds explicit
Use this lane only when shared wording needs to keep the already-landed bridge-local helper foundations distinct from the tracked pure-helper packet and the heavier deferred bridge and queue-routing buckets.

Current landed helper-foundation packet:
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` for helper-only fdinfo map-info parsing
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` for helper-only reused-map compatibility checks
- the paired survey and manifest wording that records those two helper-sized foundations truthfully

These two bridge-local helper slices are already landed on current `master`; they no longer count as pending `ready_next` promotions.

Do not widen this lane into:
- direct procfs reads
- bpffs reopen flow
- token creation
- close-on-replacement side effects
- object-model or relocation work

The next honest reopen here is drift control around those landed bridge-local foundations or a genuinely new helper-sized promotion becoming real, not pretending these already-landed packets are still the next unshipped helpers.

### 4. Deferred bridge and queue-routing lane: keep parked until repo reality changes
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

Do not smuggle this work through the shared reviewability lane, the tracked pure-helper lane, or the landed helper-foundation lane.

### 5. Object-model wall lane: blocked until the missing model surfaces exist
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

### 6. Shared summary lane: wording-only follow-through for the Phase 12 packet
Use this lane only when the shared wording surfaces drift away from the live Phase 12 libbpf ownership split.

Allowed surfaces:
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Do not use this lane to land helper code, manifest churn, or new test logic.

Keep this lane scoped to PMO release wording and shared reviewability only: it may realign the release-order note, PMO closure companion, the adjacent release-readiness note, compact release-coordination matrix, shared fallback overview, and the broad docs-root, scripts-root, or tests-root reminders with the libbpf ownership split, but it must not absorb the separate driver-only anti-overlap note or reopen driver-local Phase 12 follow-through.

Shared-summary wording must keep `Documentation/zigux/freeze-map.md` visible whenever queueing, throughput, rollback, or recovery wording shifts so the heavy-consumer ownership split stays below frozen `net/core/skbuff.c` and boundary-study-only `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c` instead of drifting into deep-core delivery claims.

## Sequencing rule
1. Re-read the shared Phase 12 libbpf survey and reviewability packet first.
2. If the drift is only wording or ownership scope, stay in the shared reviewability or shared summary lane.
3. If the drift is about the deterministic five-path helper packet, keep it inside the tracked pure-helper lane instead of widening into the bridge-local foundations.
4. If a bridge-local helper wording repair is needed, keep it smaller than the deferred bridge and queue-routing bucket and separate from the tracked pure-helper packet.
5. Keep the deferred bridge and queue-routing packet separate from both landed helper packets.
6. Keep the object-model wall separate from every smaller bridge or reviewability step.
7. Do not use this libbpf lane to absorb unrelated Phase 12 driver follow-through just because the shared build is already wired.

## Current anti-overlap correction

Today the strongest Phase 12 libbpf sequencing correction is simple:
- shared reviewability owns the survey, manifest, deterministic snapshot fixture, deterministic snapshot-digest evidence fixture, snapshot determinism replay, reviewability gate, the dedicated `tools/lib/bpf/zigux_segments/verify.zig` shard, the paired build-only checker reruns, and shared build alignment for the current libbpf packet, with the workflow-backed replay kept explicit inside that same reviewability bundle
- the tracked pure-helper lane keeps the five deterministic helper paths explicit as a smaller packet than the bridge-local helper foundations
- the two landed bridge-local helper foundations stay explicit as smaller evidence than the deferred bridge and queue-routing bucket
- the deferred bridge and queue-routing bucket stays smaller than the blocked object-model, loader, and relocation wall
- wording-only shared-summary repairs stay separate from helper logic and from the other Phase 12 driver lanes
- PMO release coordination surfaces should keep the release-order note, closure companion, adjacent release-readiness note, compact release-coordination matrix, shared fallback overview, the direct `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` preflight, the attached-toolchain Make override, the freeze-map boundary, and the libbpf reviewability packet aligned without turning this heavy-consumer lane into a driver-owner map or a closure claim

That split matches the live survey packet and keeps future scheduled runs from turning one honest heavy-consumer tranche into overlapping docs, helper, bridge, and object-model churn.

## Next bounded step

Leave this note parked unless one of four things happens:
- a shared Phase 12 summary drifts away from this ownership split
- the deterministic five-path helper packet stops matching the tracked snapshot evidence
- shared wording starts treating the two landed bridge-local helper foundations as pending `ready_next` work again
- the repo lands a real object-model foothold that changes the blocked wall itself

Until then, the safest same-family follow-through is drift control inside the shipped Phase 12 libbpf reviewability packet, not another broad survey rewrite or a speculative bridge expansion.
