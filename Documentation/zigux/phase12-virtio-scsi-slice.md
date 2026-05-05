# Phase 12 Virtio SCSI Slice

This bounded Phase 12 slice adds the first Zigux `virtio scsi` starter anchored to `drivers/scsi/virtio_scsi.c`.

The starter stays intentionally narrow:

- plans the control, event, and request virtqueue family layout from the requested request-queue count and poll-queue hint
- preserves the Linux driver rule that poll queues are clamped so at least one default request queue remains
- classifies each planned request queue as either `request` or `request_poll` with stable global virtqueue indexes starting after the control and event queues
- records the fixed event-buffer fanout used by the driver without claiming event work handling, request submission, or live transport reset completion
- freezes queue planning and event recycling intent across a lab-only transport freeze or restore boundary, then clears the old queue snapshot so the next step must replan instead of pretending virtqueues stayed live
- derives one bounded restore-sequencing summary from the frozen queue layout so the starter keeps `virtscsi_restore()` calling `find_vqs`, `virtio_device_ready()`, and event rearm reviewable without pretending to re-run `scsi_scan_host()`

This slice does not claim DMA mapping, scatter-gather command assembly, `Scsi_Host` registration, blk-mq submission, event-work recycling, TMF handling, hotplug, or live transport reset recovery.

The next honest bounded step inside the same Phase 12 lane is still to add one small probe snapshot helper that captures `virtscsi_probe()` config fields and queue-topology intent before any blk-mq submission, TMF, PM recovery, or DMA-backed queue work is attempted.
