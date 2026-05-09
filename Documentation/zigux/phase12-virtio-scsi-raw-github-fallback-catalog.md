# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This note records the read-only public GitHub fallback packet for the bounded Phase 12 `virtio_scsi` lane.

Use it when GitHub app reads are unavailable, incomplete, or rate-limited and reviewers still need to inspect the live `master` surfaces tied to `drivers/scsi/virtio_scsi.c`.

It is a fallback-read catalog, not a closure claim and not a validator-first route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-raw-github-fallback-catalog`
- `active_survey_lane: P12-L13`
- `historical_fallback_lane: P12-L09`
- scope: public tree and raw URL coverage for the shipped `virtio_scsi` starter, including the current bounded queue-window ownership summary, direct syntax-lab smoke shard, survey, build wiring, manifest, shared replay surfaces, the driver-only anti-overlap companion, the shared libbpf anti-overlap companion, the shared fallback overview, the PMO closure companion, the adjacent release-readiness note, and the compact release coordination matrix that now travel with the active release-order packet

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
- survey gate: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_survey.zig`
- survey manifest: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_manifest.json`
- scripts index: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/scripts/zigux/README.md`
- docs root packet: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/README.md`
- Linux-style replay wiring: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/Makefile`

## Current Verification Evidence

- checked on: `2026-05-09`
- latest visible public `master` head checked before this catalog refresh: `c11221dc7a68d7511ae1c69d64b3f08528287ed8` (`test(zigux): harden phase2 cross selftest coverage`)
- `PHASE12_TREE_VIEW_COUNT=18`
- `PHASE12_RAW_VIEW_COUNT=18`
- `PHASE12_VERIFIED_FILE_COUNT=18`
- verification method: public GitHub commits-page readback for the visible `master` head, public GitHub raw fallback readback for the bounded packet, and authenticated blob-identity readback for every covered file listed below
- current blob identities for the covered packet:
  - `drivers/scsi/virtio_scsi.zig`: `3c26a8159be399aac0f044d6305f3e5f4a0be244`
  - `Documentation/zigux/phase12-virtio-scsi-slice.md`: `4cd01f078131bb3d7dd151d4c971d41e81aaa884`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`: `a9baf66c80753959b0a98b5500066a619b36f338`
  - `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`: `355c2a58988f3cd6dcd828668f56ef2945285a7a`
  - `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`: `ea4eb520446bb321625c30c098e2d465fcac0bb2`
  - `Documentation/zigux/phase12-raw-github-coverage-survey.md`: `60d70445e81a2bca16efd02bef5eb65acda9c9a3`
  - `Documentation/zigux/phase12-release-closure-checklist.md`: `bdc7971f80ac4d8d69f339ca348c5fdedf346539`
  - `Documentation/zigux/phase12-release-readiness-survey.md`: `ffb31ca1a67cee06654eb538353c4c9f8f8e7ef6`
  - `Documentation/zigux/phase12-release-coordination-matrix.md`: `42c64fa9314b2d655a2deedbeca12056e130fbb2`
  - `zigux/tests/README.md`: `0753a6777cec92fa5985263a7f64f93820694575`
  - `zigux/tests/phase12_build.zig`: `be8a03ec689903142e917ba874803520b7bbf056`
  - `zigux/tests/phase12_virtio_scsi.zig`: `b4fcae1fb70d3aedd6b6599d8211bcf68a66aca4`
  - `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`: `1fdcbe06efff486e7f97fb46064db7a48f4d018e`
  - `zigux/tests/phase12_virtio_scsi_survey.zig`: `543c6e36c17ffdc5bce9c063f98eada469417b94`
  - `zigux/tests/phase12_virtio_scsi_manifest.json`: `f0f911857bd56d7dbf206c3ccd2357ea5059a14f`
  - `scripts/zigux/README.md`: `b1e6311ca8fa810dec67052bdd20155dbfd15b95`
  - `Documentation/zigux/README.md`: `6fa7fa021eb7997de31f63700b8bca2282fa53c9`
  - `zigux/Makefile`: `cfb5a1ebd283c5f86ccc264ceccaf704fd8c47b5`
- bounded coverage result: the current public tree and raw fallback packet still resolves cleanly for all 18 listed surfaces, and the shipped fallback note still matches the live `virtio_scsi` release-adjacent packet on `master`

## Shared replay reminder

The shipped Phase 12 packet on `master` still keeps the shared smoke-first replay order below.

- current virtio_scsi smoke packet surfaces: `zigux/tests/phase12_virtio_scsi.zig` and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- current degraded-read reminder: those same starter-facing surfaces now keep the landed queue-window ownership summary explicit, so the control and event queue gap plus the default-versus-poll request-queue ranges stay reviewable here without claiming blk-mq queue mapping or live request ownership

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

If the bounded `virtio_scsi` packet gains or drops a shipped Phase 12 surface, or if the shipped starter-facing queue-window or recovery-summary wording changes inside that existing packet, update this catalog in the same change so fallback inspection keeps matching the live reviewable packet on `master`.