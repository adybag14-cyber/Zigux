# Phase 12 Virtio SCSI Slice

This bounded Phase 12 slice adds the first Zigux `virtio scsi` starter anchored to `drivers/scsi/virtio_scsi.c`.

The starter stays intentionally narrow:

- plans the control, event, and request virtqueue family layout from the requested request-queue count and poll-queue hint
- preserves the Linux driver rule that poll queues are clamped so at least one default request queue remains
- classifies each planned request queue as either `request` or `request_poll` with stable global virtqueue indexes starting after the control and event queues
- captures a small `virtscsi_probe()` config snapshot for `num_queues`, `seg_max`, `cmd_per_lun`, `max_target`, `max_lun`, and `max_sectors`, then derives the queue-topology intent after the Linux-style CPU-count and blk-mq queue caps are applied
- records the fixed event-buffer fanout used by the driver without claiming event work handling, request submission, or transport reset completion

This slice does not claim DMA mapping, scatter-gather command assembly, `Scsi_Host` registration, blk-mq submission, event-work recycling, TMF handling, hotplug, or live transport reset recovery.

The next honest bounded step inside the same Phase 12 lane is to add one small host-limit handoff helper that records how the probe snapshot would feed `sg_tablesize`, `can_queue`, `cmd_per_lun`, `max_sectors`, `max_lun`, `max_id`, and `nr_maps` before any blk-mq submission, TMF, PM recovery, or DMA-backed queue work is attempted.
