# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This note records the read-only public GitHub fallback packet for the bounded Phase 12 `virtio_scsi` lane.

Use it when GitHub app reads are unavailable, incomplete, or rate-limited and reviewers still need to inspect the live `master` surfaces tied to `drivers/scsi/virtio_scsi.c`.

It is a fallback-read catalog, not a closure claim and not a validator-first route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-raw-github-fallback-catalog`
- `active_survey_lane: P12-L13`
- `historical_fallback_lane: P12-L09`
- scope: public tree and raw URL coverage for the shipped `virtio_scsi` starter, including the current bounded queue-window ownership summary, direct syntax-lab smoke shard, focused repeated-rollback gate, survey, build wiring, manifest, shared replay surfaces, the driver-only anti-overlap companion, the shared libbpf anti-overlap companion, the shared fallback overview, the PMO closure companion, the adjacent release-readiness note, and the compact release coordination matrix that now travel with the active release-order packet

## Tree views

- driver starter: `https://github.com/adybag14-cyber/Zigux/blob/master/drivers/scsi/virtio_scsi.zig`
- slice note: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-virtio-scsi-slice.md`
- survey note: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-virtio-scsi-survey.md`
- driver-only anti-overlap companion: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shared libbpf anti-overlap companion: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- shared fallback overview: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-raw-github-coverage-survey.md`
- PMO closure companion: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-closure-checklist.md`
- adjacent release-readiness note: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-readiness-survey.md`
- compact release coordination matrix: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-coordination-matrix.md`
- shared tests index: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/README.md`
- shared build wiring: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_build.zig`
- direct test gate: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi.zig`
- direct syntax-lab smoke shard: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- focused repeated-rollback gate: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`
- survey gate: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_survey.zig`
- survey manifest: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_manifest.json`
- scripts index: `https://github.com/adybag14-cyber/Zigux/blob/master/scripts/zigux/README.md`
- docs root packet: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/README.md`
- Linux-style replay wiring: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/Makefile`

## Raw file views

- driver starter: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/scsi/virtio_scsi.zig`
- slice note: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-slice.md`
- survey note: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-survey.md`
- driver-only anti-overlap companion: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shared libbpf anti-overlap companion: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- shared fallback overview: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-raw-github-coverage-survey.md`
- PMO closure companion: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-closure-checklist.md`
- adjacent release-readiness note: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-readiness-survey.md`
- compact release coordination matrix: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-coordination-matrix.md`
- shared tests index: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/README.md`
- shared build wiring: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_build.zig`
- direct test gate: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi.zig`
- direct syntax-lab smoke shard: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- focused repeated-rollback gate: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`
- survey gate: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_survey.zig`
- survey manifest: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_manifest.json`
- scripts index: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/scripts/zigux/README.md`
- docs root packet: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/README.md`
- Linux-style replay wiring: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/Makefile`

## Current Verification Evidence

- checked on: `2026-05-10`
- latest visible public `master` head checked before this catalog refresh: `3ea8f93f1e475fcfa89a5e46940cc82be01f2971` (`docs(zigux): guard phase13 contributor sync against closure drift`)
- `PHASE12_TREE_VIEW_COUNT=19`
- `PHASE12_RAW_VIEW_COUNT=19`
- `PHASE12_VERIFIED_FILE_COUNT=19`
- verification method: public GitHub commits-page readback for the visible `master` head, public GitHub raw fallback readback for the bounded packet, and authenticated blob-identity readback for every covered file listed below
- current blob identities for the covered packet:
  - `drivers/scsi/virtio_scsi.zig`: `5f76c9e23a470545238df3ec10db60b91ab12786`
  - `Documentation/zigux/phase12-virtio-scsi-slice.md`: `a5c85a0a2326237278217c4a86744adb239c71c4`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`: `73269ae39f8381b9ea3b559ecdbe9ec09b9886d1`
  - `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`: `2ffc4c8c7cb64549ba7905b5c7ade3d6f606c5a9`
  - `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`: `ff935dc32370d61080062b4de8134b51449ebbb2`
  - `Documentation/zigux/phase12-raw-github-coverage-survey.md`: `3a0e7c32ccc27c870272db9d1d920c563c3467b6`
  - `Documentation/zigux/phase12-release-closure-checklist.md`: `0deddc05ac992935f6a10ccc65df444683d67847`
  - `Documentation/zigux/phase12-release-readiness-survey.md`: `32084a128911d4062fe1fe4d2d40d6cec4682469`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`: `6ca8d9e0d3f198f0f83f863ce6b2fa0790744cf1`
  - `zigux/tests/README.md`: `705ed8ce93c79802ea1978e1e8013a053b7c7b77`
  - `zigux/tests/phase12_build.zig`: `be8a03ec689903142e917ba874803520b7bbf056`
  - `zigux/tests/phase12_virtio_scsi.zig`: `00f25168064832145bc5a1d70221bc5e432084b5`
  - `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`: `fb036ca89d9e2ce547756781dc0d3e1507620abc`
  - `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`: `514bea34a366e74e3aa0114c3f7afe98b696502f`
  - `zigux/tests/phase12_virtio_scsi_survey.zig`: `33f694e21d02f93995b67e7273e27727ce9ec735`
  - `zigux/tests/phase12_virtio_scsi_manifest.json`: `30b6878de70003eb2f893cb3b16b65441017dbc7`
  - `scripts/zigux/README.md`: `efc02077ea90a8ac66aa62fada196b6a7802d704`
  - `Documentation/zigux/README.md`: `65f831044b3a89b0c785575ccc086f9c5598b5a2`
  - `zigux/Makefile`: `06d4605ed21ec25e9c6793d0a713b72852ad1822`
- bounded coverage result: the current public tree and raw fallback packet still resolves cleanly for all 19 listed surfaces, and the shipped fallback note still matches the live `virtio_scsi` release-adjacent packet on `master`

## Shared replay reminder

The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.

- current virtio_scsi smoke packet surfaces: `zigux/tests/phase12_virtio_scsi.zig` and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- current degraded-read reminder: those same starter-facing surfaces now keep the landed queue-window ownership summary explicit, so the control and event queue gap plus the default-versus-poll request-queue ranges stay reviewable here without claiming blk-mq queue mapping or live request ownership
- focused rollback reminder: `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` is a driver-local readback surface for the repeated restore and rollback boundary; it stays visible in this fallback catalog without being rounded up into the shared smoke-set count or a separate Phase 12 entrypoint

## Roadmap gap snapshot

Use the fallback packet to keep the roadmap comparison honest, not just reachable.

- landed bounded starter surfaces: the shipped `virtio_scsi` packet now exposes the queue-window summary, probe-config snapshot, pre-registration host-shape summary, repeated transport-reset recovery-generation gate, restore queue rebind summary, request-queue restart summary, request-queue ownership summary, recovery event-rearm summary, restore-time event-buffer ownership summary, rollback summary, and the focused repeated-rollback gate as reviewable driver-local evidence.
- still-blocked complex-driver roadmap gap: this fallback route must still describe command submission, event completion, TMF flow, `scsi_add_host()`, `scsi_scan_host()`, blk-mq queue mapping, PM freeze or restore callback wiring, and DMA-backed virtqueue ownership as unported runtime work rather than implying production SCSI HBA parity.
- survey-owner split: the active gap judgment lives with `P12-L13` in `Documentation/zigux/phase12-virtio-scsi-survey.md` and `zigux/tests/phase12_virtio_scsi_manifest.json`; this historical `P12-L09` note should mirror that bounded gap snapshot for degraded reads, but it must not become a second owner lane.

1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`
5. If the local runtime does not provide `zig` on `PATH`, keep the same smoke-first order and rerun the shipped Make routes with an attached toolchain override instead of inventing a new Phase 12 entrypoint.
   - `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
   - `make -C zigux phase12 ZIG=<attached-zig-path>`
   - This is an environment override for the existing replay packet, not a validator-first or `phase12-validate` route.

Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether those same shipped surfaces are close enough to describe the active Phase 12 tranche as release-closed.

Keep `Documentation/zigux/phase12-release-readiness-survey.md` visible beside this fallback catalog, the PMO closure companion, and the compact release coordination matrix so the shared smoke-first release posture and build-only replay boundary stay tied to the same active packet instead of drifting into a separate readiness-only route.

`Documentation/zigux/phase12-complex-driver-lane-sequencing.md` should stay visible beside this fallback catalog and the compact release coordination matrix so the `virtio_scsi` packet stays separate from `nvme_pci` and `virtio_net` even while all three lanes share the same four-step replay order.

`Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` should stay visible beside this fallback catalog, the PMO closure companion, and the compact release coordination matrix so the non-driver libbpf ownership split remains reviewable beside the shared release packet instead of disappearing behind this driver-local fallback note.

`Documentation/zigux/phase12-raw-github-coverage-survey.md` should stay visible beside this fallback catalog so the two commit-pinned artifacts plus two shared-tree-only anchors split remains reviewable without turning this driver-local note into a broader fallback-ownership summary.

`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this fallback catalog, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this fallback catalog into a second sequencing document.

The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`, and `.github/workflows/zigux-bootstrap.yml` reruns that checker so this fallback wording stays aligned with the shipped PMO release packet.

This catalog should stay read-only and should not be used to imply an unshipped `validate-phase12.py`, any `check-phase12-*.py` packet, or a `make -C zigux phase12-validate` target.

## Update rule

If the bounded `virtio_scsi` packet gains or drops a shipped Phase 12 surface, if the shipped starter-facing queue-window or recovery-summary wording changes inside that existing packet, if the focused repeated-rollback gate moves, or if the survey-owned roadmap-gap snapshot changes, update this catalog in the same change so fallback inspection keeps matching the live reviewable packet on `master`.