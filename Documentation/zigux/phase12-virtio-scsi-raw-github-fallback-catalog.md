# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This note records the read-only public GitHub fallback packet for the bounded Phase 12 `virtio_scsi` lane.

Use it when GitHub app reads are unavailable, incomplete, or rate-limited and reviewers still need to inspect the live `master` surfaces tied to `drivers/scsi/virtio_scsi.c`.

It is a fallback-read catalog, not a closure claim and not a validator-first route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-raw-github-fallback-catalog`
- `active_survey_lane: P12-L13`
- `historical_fallback_lane: P12-L09`
- scope: public tree and raw URL coverage for the shipped `virtio_scsi` starter, survey, build wiring, manifest, and shared replay surfaces

## Tree views

- driver starter: `https://github.com/adybag14-cyber/Zigux/blob/master/drivers/scsi/virtio_scsi.zig`
- slice note: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-virtio-scsi-slice.md`
- survey note: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-virtio-scsi-survey.md`
- shared tests index: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/README.md`
- shared build wiring: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_build.zig`
- direct test gate: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi.zig`
- survey gate: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_survey.zig`
- survey manifest: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_virtio_scsi_manifest.json`
- scripts index: `https://github.com/adybag14-cyber/Zigux/blob/master/scripts/zigux/README.md`
- docs root packet: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/README.md`
- Linux-style replay wiring: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/Makefile`

## Raw file views

- driver starter: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/scsi/virtio_scsi.zig`
- slice note: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-slice.md`
- survey note: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-survey.md`
- shared tests index: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/README.md`
- shared build wiring: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_build.zig`
- direct test gate: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi.zig`
- survey gate: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_survey.zig`
- survey manifest: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_virtio_scsi_manifest.json`
- scripts index: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/scripts/zigux/README.md`
- docs root packet: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/README.md`
- Linux-style replay wiring: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/Makefile`

## Shared replay reminder

The shipped Phase 12 release order on `master` remains:

1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`

The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`, and `.github/workflows/zigux-bootstrap.yml` reruns that checker so this fallback wording stays aligned with the shipped PMO release packet.

This catalog should stay read-only and should not be used to imply an unshipped `validate-phase12.py`, any `check-phase12-*.py` packet, or a `make -C zigux phase12-validate` target.

## Update rule

If the bounded `virtio_scsi` packet gains or drops a shipped Phase 12 surface, update this catalog in the same change so fallback inspection keeps matching the live reviewable packet on `master`.
