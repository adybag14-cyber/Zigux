# Phase 12 Release Sequencing

This note records the ordered release path for the active bounded Phase 12 tranche.

It is a release-coordination artifact, not a closure claim.

## Current posture
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- direct smoke preflight entrypoint: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
- focused smoke preflight entrypoint: `make -C zigux phase12-smoke`
- shared build replay entrypoint: `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- Linux-style replay entrypoint: `make -C zigux phase12`
- PMO closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shipped shared release surfaces on `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, the committed Phase 12 manifests under `zigux/tests/`, and `tools/lib/bpf/zigux_segments/manifest.json`
- current public fallback split: two commit-pinned artifacts (`Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`) and two shared-tree-only anchors (`virtio_net`, `libbpf`)
- current shared fallback overview note: `Documentation/zigux/phase12-raw-github-coverage-survey.md` records that mixed split as one bounded Phase 12 degraded-read map and must stay aligned with the two commit-pinned artifacts without turning itself into a third commit-pinned fallback artifact
- current driver-local doc split: `nvme_pci` and `virtio_scsi` each ship a dedicated slice note, while `virtio_net` still truthfully remains survey-backed without a separate `Documentation/zigux/phase12-virtio-net-slice.md` file on `master`
- current complex-driver owner split: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` keeps `virtio_net`, `nvme_pci`, and `virtio_scsi` separate from each other and from the non-driver libbpf packet even though they share the same smoke-plus-build replay routes

## Release order
1. Reconfirm the release packet surfaces before any replay claim.
   - Re-read `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and this sequencing note together.
   - Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when assessing whether those shipped surfaces are close enough to describe the tranche as release-closed.
   - These surfaces must continue to agree that the shared replay route on `master` is the bounded `phase12_build.zig` plus `make -C zigux phase12` path, while `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml` keep the build-only contract fail-closed rather than implying an unshipped validator stack, while the public fallback split stays explicit as two commit-pinned artifacts for `nvme_pci` and `virtio_scsi` plus two shared-tree-only anchors for `virtio_net` and `libbpf`, and while `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` keeps the three complex-driver lanes distinct from each other instead of flattening them into one shared driver bucket.
2. Run the focused smoke preflight before the full tranche replay.
   - `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
   - `make -C zigux phase12-smoke`
   - These remain the shipped narrow replay routes for the direct `nvme_pci`, `virtio_net`, and `virtio_scsi` test bodies plus the focused syntax-lab shard, so PMO sequencing can catch obvious packet drift before the broader survey-backed replay.
3. Run the shared Phase 12 build replay.
   - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
   - This remains the shipped tranche-wide Zig replay surface for the bounded `virtio_net`, `nvme_pci`, `virtio_scsi`, and libbpf survey packet.
4. Run the Linux-style entrypoint last.
   - `make -C zigux phase12`
   - This should remain the summary replay route rather than the only place release coordination is inferred.

## Owner map
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` is the driver-only anti-overlap companion for `virtio_net`, `nvme_pci`, and `virtio_scsi`.
- `BPF Tooling Lane`: bounded libbpf helper packet against `tools/lib/bpf/libbpf.c`
- `PMO / Release Management`: release-facing sequencing, tranche-readiness wording, and cross-surface coordination artifacts

## Rollback and Reversible-Delivery Reminder
- The current storage-lane rollback drill is a bounded `virtio_scsi` lab surface, not a tranche-wide recovery claim.
- `Documentation/zigux/phase12-virtio-scsi-slice.md` now records a lab-only freeze or restore boundary that blocks queue planning while transport is frozen, clears the old queue snapshot after restore, and keeps the `virtscsi_restore()` `find_vqs` plus `virtio_device_ready()` sequencing reviewable without claiming `scsi_scan_host()` replay or broad transport-reset parity.
- Release-facing PMO notes should describe that shipped storage-lane evidence as reversible-delivery scaffolding for the roadmap's recovery-parity direction, not as closure-ready runtime recovery, release readiness, or a validator-first gate.

## Current blocker to closure

The shared Phase 12 replay route on `master` is narrower than some older PMO notes implied.

Today the shipped release packet is centered on:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- `Documentation/zigux/phase12-release-closure-checklist.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-build-only-phase12-surface.py`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/README.md`
- `zigux/tests/phase12_build.zig`
- `zigux/Makefile`
- the committed Phase 12 manifests under `zigux/tests/`
- `tools/lib/bpf/zigux_segments/manifest.json`
- the committed survey-backed test modules under `zigux/tests/`

The remaining release-discipline gap is still a PMO truthfulness problem rather than a closure-ready checkpoint:
- `zigux/tests/README.md` now keeps `Documentation/zigux/phase12-release-closure-checklist.md` visible from the shared Phase 12 tests-root packet, so the older tests-root reminder is no longer the live blocker on `master`
- `scripts/zigux/README.md` now also keeps `Documentation/zigux/phase12-release-closure-checklist.md` visible from the shared Phase 12 scripts-root packet, so the older scripts-root reminder is no longer the live blocker on `master`
- the two commit-pinned fallback notes now also keep `Documentation/zigux/phase12-release-closure-checklist.md` visible beside the shipped four-step release order, so their remaining PMO role is cross-surface drift control rather than another missing companion reminder
- the shared fallback overview note `Documentation/zigux/phase12-raw-github-coverage-survey.md` now also has to stay aligned with that same two-artifact-plus-two-anchor split, so PMO drift control should keep rereading it beside the driver-local fallback notes rather than leaving the mixed split implied from those narrower artifacts alone
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` now carries the driver-only anti-overlap map, so release-planning drift control should reread it beside the PMO packet instead of letting the three complex-driver lanes collapse back into one shared owner bucket
- `scripts/zigux/check-build-only-phase12-surface.py` is a shipped build-only contract checker, not a broader validator-first release gate
- `.github/workflows/zigux-bootstrap.yml` reruns that checker's self-test plus the live checker and should stay described as build-only contract enforcement rather than a broader validator-first release packet
- there is no shipped shared `scripts/zigux/validate-phase12.py`, no `check-phase12-*.py` release packet, and no `make -C zigux phase12-validate` target on `master`
- the bounded `virtio_scsi` rollback drill is reviewable release evidence, but it must stay described as a lab-only storage anchor rather than a tranche-wide recovery checkpoint
- the checker-local closure-companion repair is already landed on `master`: `scripts/zigux/check-build-only-phase12-surface.py` now explicitly pins `Documentation/zigux/phase12-release-closure-checklist.md` inside its fail-closed marker set
- `Documentation/zigux/README.md` already carries `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` and `Documentation/zigux/phase12-raw-github-coverage-survey.md` beside the active Phase 12 packet, so the next remaining same-lane drift has moved to the shared review prompt: `Documentation/zigux/review-checklist.md` still does not keep those two coordination surfaces explicit inside its shared Phase 12 checklist question even though this sequencing note, the PMO closure companion, and the shipped Phase 12 packet already treat them as active release-management surfaces on `master`
- keep this sequencing note aligned with `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and the bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback-drill wording instead of reopening already-landed naming repairs or inventing removed validator surfaces
- if the lane reopens for another degraded-workflow drift, start by diffing those shipped packet surfaces, rereading `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, and rerunning `scripts/zigux/check-build-only-phase12-surface.py` before widening into any driver-local or helper-local Phase 12 work
- release planning must therefore keep naming only the shipped smoke preflight routes, the shared build-and-make replay path, the narrow build-only contract checker, the PMO closure companion, the shared fallback-overview note, the driver-only anti-overlap companion, and the bounded storage rollback drill until a broader validator-first or runtime-recovery Phase 12 packet actually lands

## Closure conditions

Phase 12 should not be described as release-closed until all of the following are true:
1. `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, this sequencing note, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, and `Documentation/zigux/phase12-raw-github-coverage-survey.md` still agree on the same shipped Phase 12 replay surface.
2. `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` all remain explicit and green.
3. The approved four-anchor packet remains explicit and honest across the Phase 12 survey notes, the committed manifests under `zigux/tests/`, `tools/lib/bpf/zigux_segments/manifest.json`, and the bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback-drill wording.
4. The public fallback split is still described honestly, with `Documentation/zigux/phase12-raw-github-coverage-survey.md` keeping the shared mixed overview explicit and `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` plus `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` staying the only commit-pinned fallback artifacts rather than rounded up into implied commit-pinned coverage for every anchor.
5. Any future validator-first Phase 12 release gate is published on `master` before PMO notes describe it as part of the active release route, while `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml` remain scoped to the shipped build-only contract.

## Next bounded PMO step

Keep the current Phase 12 PMO packet truthfulness-first.

The checker-local closure-companion repair and the docs-root coordination-surface sync are already landed on `master`, so the next bounded same-lane follow-through should stay inside the shared review surface instead of reopening those finished steps:
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py`, then use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion to update `Documentation/zigux/review-checklist.md` so the shared Phase 12 checklist question explicitly carries `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` and `Documentation/zigux/phase12-raw-github-coverage-survey.md` beside the already-listed sequencing note, closure checklist, driver-local notes, scripts-root, tests-root, workflow-backed checker, and smoke-plus-build replay route
- after that review-checklist sync lands, extend `scripts/zigux/check-build-only-phase12-surface.py` so its `Documentation/zigux/review-checklist.md` marker set also fails closed on those two coordination surfaces before widening into another PMO packet reread
- if the lane reopens for another degraded-workflow drift after those two shared-surface updates land, start by diffing `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` against this sequencing note plus `Documentation/zigux/phase12-release-closure-checklist.md` before widening into any new PMO claim
- after any real shared-surface update lands, rerun `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` so the PMO closure companion stays tied to shipped replay routes instead of reopening validator-first or runtime-recovery claims

If a validator-first release route is proposed later, land the actual shipped file and replay surface first, then update the release-planning notes to name it exactly once beside the existing `phase12_build.zig`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, and `make -C zigux phase12` path.
