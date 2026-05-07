# Phase 12 Raw GitHub Coverage Survey

This note records the shared read-only public GitHub fallback split for the active bounded Phase 12 tranche.

Use it when GitHub app reads are unavailable, incomplete, or rate-limited and reviewers still need one truthful map of which shipped Phase 12 surfaces are commit-pinned fallback artifacts versus shared-tree-only anchors on `master`.

It is a fallback-read overview, not a closure claim, not a validator-first route, and not a third commit-pinned fallback artifact.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=raw-github-coverage-survey`
- scope: shared fallback-read coverage for the shipped `nvme_pci`, `virtio_net`, `virtio_scsi`, and libbpf Phase 12 packet plus the compact release-coordination matrix, PMO closure companion, and shared replay surfaces that travel with the active release-order packet
- commit-pinned fallback artifacts: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- shared-tree-only anchors: `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md`

## Coverage split

### Commit-pinned fallback artifacts
- `nvme_pci`: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- `virtio_scsi`: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`

Those two notes are the only shipped Phase 12 fallback artifacts whose job is to catalog both tree and raw public GitHub URLs for one driver-local packet.

### Shared-tree-only anchors
- `virtio_net`: `Documentation/zigux/phase12-virtio-net-survey.md`
- libbpf: `Documentation/zigux/phase12-libbpf-segment-survey.md`

Those two notes remain truthful shared-tree-only anchors on `master`. They are reviewable public repo surfaces, but they are not commit-pinned fallback artifacts and should not be described as if they owned the same raw-URL catalog role as the `nvme_pci` and `virtio_scsi` notes.

## Shared replay reminder

The shipped Phase 12 packet on `master` still keeps the same four-step smoke-first replay order used by the PMO sequencing and closure companion notes.

- current smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`

1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`

Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether those same shipped surfaces are close enough to describe the active Phase 12 tranche as release-closed.

`Documentation/zigux/phase12-release-coordination-matrix.md` should stay visible beside this shared fallback overview, the PMO closure companion, and the longer sequencing note so the lane-owner split, two-artifact-plus-two-anchor fallback split, and smoke-set summary remain reviewable together without turning this survey into a second sequencing document.

`zigux/tests/README.md` and `Documentation/zigux/phase12-release-sequencing.md` should keep this shared fallback overview visible beside that same PMO companion so the two-artifact-plus-two-anchor split does not disappear from the shared release packet while the narrower driver-local fallback notes stay unchanged.

`Documentation/zigux/phase12-release-sequencing.md` and `Documentation/zigux/phase12-release-coordination-matrix.md` should stay aligned on that same split so the compact coordination view remains reviewable without pretending the tests-root packet already owns the matrix reminder directly.

`Documentation/zigux/phase12-complex-driver-lane-sequencing.md` remains the separate driver-only anti-overlap companion for `virtio_net`, `nvme_pci`, and `virtio_scsi`, so this shared fallback overview should be reread beside that lane map instead of letting the mixed fallback split blur those three driver lanes back together.

The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`, and `.github/workflows/zigux-bootstrap.yml` reruns that checker so this shared fallback-overview wording stays aligned with the shipped PMO release packet.

This overview should stay read-only and should not be used to imply an unshipped `validate-phase12.py`, any `check-phase12-*.py` packet, a focused libbpf-only replay route, or a `make -C zigux phase12-validate` target.

## Update rule

If the bounded Phase 12 packet gains or drops a shared-tree-only anchor or a commit-pinned fallback artifact, update this overview in the same change so the shared fallback split keeps matching the live reviewable packet on `master`.
