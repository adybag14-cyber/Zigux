# Phase 12 Virtio SCSI Slice

This bounded Phase 12 slice adds the first Zigux `virtio scsi` starter anchored to `drivers/scsi/virtio_scsi.c`.

The starter stays intentionally narrow:

- plans the control, event, and request virtqueue family layout from the requested request-queue count and poll-queue hint
- preserves the Linux driver rule that poll queues are clamped so at least one default request queue remains
- classifies each planned request queue as either `request` or `request_poll` with stable global virtqueue indexes starting after the control and event queues
- records one bounded `virtscsi_probe()` config snapshot through `num_queues`, `seg_max`, `cmd_per_lun`, `max_target`, `max_lun`, `max_sectors`, and the derived control or event versus request virtqueue layout before any blk-mq submission or DMA-backed queue work
- records the fixed event-buffer fanout used by the driver and derives one bounded restore-time event-buffer ownership summary so the event queue remains reserved across freeze and restore without claiming event work handling, request submission, or live transport reset completion
- freezes queue planning and event recycling intent across a lab-only transport freeze or restore boundary, then clears the old queue snapshot so the next step must replan instead of pretending virtqueues stayed live
- derives one bounded restore-sequencing summary from the frozen queue layout so the starter keeps `virtscsi_restore()` calling `find_vqs`, `virtio_device_ready()`, and event rearm reviewable without pretending to re-run `scsi_scan_host()`

This slice does not claim DMA mapping, scatter-gather command assembly, `Scsi_Host` registration, blk-mq submission, event-work recycling, TMF handling, hotplug, or live transport reset recovery.

The shared Phase 12 packet now keeps the direct smoke preflight explicit here too: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12-smoke` rerun this bounded `virtio scsi` starter before the broader survey-backed replay, so the slice should stay aligned with that smoke-plus-build order instead of leaving it implicit in `zigux/tests/phase12_build.zig`, `zigux/Makefile`, or `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` alone.

The next honest bounded step inside the same Phase 12 lane is no longer another queue-family-only helper. Keep this slice parked until the roadmap approves queue ownership, SCSI host registration, or DMA-backed queue work beyond the now-landed `virtscsi_probe()` config snapshot.