# Phase 12 Raw GitHub Coverage Survey

This note records the shared read-only public GitHub fallback split for the active bounded Phase 12 tranche.

Use it when GitHub app reads are unavailable, incomplete, or rate-limited and reviewers still need one truthful map of which shipped Phase 12 surfaces are commit-pinned fallback artifacts versus shared-tree-only anchors on `master`.

It is a fallback-read overview, not a closure claim, not a validator-first route, and not a third commit-pinned fallback artifact.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=raw-github-coverage-survey`
- scope: shared fallback-read coverage for the shipped `nvme_pci`, `virtio_net`, `virtio_scsi`, and libbpf Phase 12 packet plus the compact release-coordination matrix, PMO closure companion, the two anti-overlap companions, the freeze-boundary guard, and shared replay surfaces that travel with the active release-order packet
- commit-pinned fallback artifacts: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- `PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`
- shared-tree-only anchors: `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`
- deterministic libbpf artifact companions: `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, and `zigux/tests/phase12_libbpf_snapshot_determinism.zig`
- driver-only anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- freeze-boundary guard: `Documentation/zigux/freeze-map.md`; queueing, throughput, rollback, and recovery wording in this shared fallback overview must stay below active delivery claims against frozen `net/core/skbuff.c` and below boundary-study-only `kernel/workqueue.c` plus `kernel/trace/ring_buffer.c`

## Coverage split

### Commit-pinned fallback artifacts
- `nvme_pci`: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- `virtio_scsi`: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`

Those two notes are the only shipped Phase 12 fallback artifacts whose job is to catalog both tree and raw public GitHub URLs for one driver-local packet.

### Shared-tree-only anchors
- `virtio_net`: `Documentation/zigux/phase12-virtio-net-survey.md`
- libbpf: `Documentation/zigux/phase12-libbpf-segment-survey.md`

Those two notes remain truthful shared-tree-only anchors on `master`. They are reviewable public repo surfaces, but they are not commit-pinned fallback artifacts and should not be described as if they owned the same raw-URL catalog role as the `nvme_pci` and `virtio_scsi` notes.

## Shared public path map

### Tree views
- shared fallback overview: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-raw-github-coverage-survey.md`
- commit-pinned `nvme_pci` fallback map: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- commit-pinned `virtio_scsi` fallback catalog: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- shared-tree-only `virtio_net` anchor: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-virtio-net-survey.md`
- shared-tree-only libbpf anchor: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-libbpf-segment-survey.md`
- release-order authority: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-sequencing.md`
- PMO closure companion: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-closure-checklist.md`
- adjacent release-readiness note: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-readiness-survey.md`
- compact release coordination matrix: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-coordination-matrix.md`
- driver-only anti-overlap companion: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shared libbpf anti-overlap companion: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- freeze-boundary guard: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/freeze-map.md`

### Raw file views
- shared fallback overview: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-raw-github-coverage-survey.md`
- commit-pinned `nvme_pci` fallback map: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- commit-pinned `virtio_scsi` fallback catalog: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- shared-tree-only `virtio_net` anchor: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-net-survey.md`
- shared-tree-only libbpf anchor: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-libbpf-segment-survey.md`
- release-order authority: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-sequencing.md`
- PMO closure companion: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-closure-checklist.md`
- adjacent release-readiness note: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-readiness-survey.md`
- compact release coordination matrix: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-coordination-matrix.md`
- driver-only anti-overlap companion: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shared libbpf anti-overlap companion: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- freeze-boundary guard: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/freeze-map.md`

## Shared replay reminder

The shipped Phase 12 packet on `master` still keeps the same four-step smoke-first replay order used by the PMO sequencing and closure companion notes.

That same shared replay reminder still includes the attached-toolchain fallback when `zig` is absent from `PATH`.

- current smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- `PHASE12_SHARED_SMOKE_SURFACE_COUNT=6`
- deterministic libbpf artifact companions that travel with the same shared release packet: `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, and `zigux/tests/phase12_libbpf_snapshot_determinism.zig`
- `PHASE12_LIBBPF_TRACKED_HELPER_COUNT=5`

1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`
5. If the local runtime does not provide `zig` on `PATH`, keep the same smoke-first order and rerun the shipped Make routes with an attached toolchain override instead of inventing a new Phase 12 entrypoint.
   - `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
   - `make -C zigux phase12 ZIG=<attached-zig-path>`
   - This is an environment override for the existing replay packet, not a validator-first or `phase12-validate` route.

Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether those same shipped surfaces are close enough to describe the active Phase 12 tranche as release-closed.

Keep `Documentation/zigux/phase12-release-readiness-survey.md` visible beside this shared fallback overview, the PMO closure companion, and `Documentation/zigux/phase12-release-coordination-matrix.md` so adjacent tranche-readiness wording stays tied to the same two-artifact-plus-two-anchor split, the deterministic libbpf artifact companions, and the smoke-first release packet instead of drifting into its own broader route.

`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this shared fallback overview, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, deterministic libbpf artifact companions, and smoke-set summary remain reviewable together without turning this survey into a second sequencing document.

`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/freeze-map.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, and `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should keep this shared fallback overview visible beside that same PMO companion so the two-artifact-plus-two-anchor split, the deterministic libbpf artifact companions, the freeze-boundary reminder, and the driver-only versus shared-libbpf anti-overlap map do not disappear from the shared release packet while the narrower driver-local fallback notes stay unchanged.

`Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, and `zigux/tests/README.md` should stay aligned on that same split so the compact coordination view remains reviewable while the tests-root packet keeps the matrix reminder explicit.

`Documentation/zigux/freeze-map.md` should stay visible beside this shared fallback overview whenever queueing, throughput, rollback, or recovery wording shifts so the two commit-pinned fallback artifacts, two shared-tree-only anchors, deterministic libbpf artifact companions, and smoke-first replay packet do not get rounded up into deep-core delivery claims.

`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should be reread beside this shared fallback overview whenever shared Phase 12 libbpf ownership wording changes so the fallback split does not blur the shared reviewability lane, the tracked pure-helper lane, the landed helper-foundation lane, the deferred bridge and queue-routing lane, and the blocked object-model wall back into one vague `libbpf` bucket.

`Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion for `virtio_net`, `nvme_pci`, and `virtio_scsi`, so this shared fallback overview should be reread beside that lane map instead of letting the mixed fallback split blur those three driver lanes back together.

The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`, and the direct PMO drift-control reruns are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` plus `python3 scripts/zigux/check-build-only-phase12-surface.py` before or beside the workflow-backed replay in `.github/workflows/zigux-bootstrap.yml`, so this shared fallback-overview wording stays aligned with the shipped PMO release packet.

This overview should stay read-only and should not be used to imply an unshipped `validate-phase12.py`, any `check-phase12-*.py` packet, a focused libbpf-only replay route, or a `make -C zigux phase12-validate` target.

## Update rule

If the bounded Phase 12 packet gains or drops a shared-tree-only anchor, a commit-pinned fallback artifact, or one of the deterministic libbpf artifact companions, update this overview in the same change so the shared fallback split keeps matching the live reviewable packet on `master`.