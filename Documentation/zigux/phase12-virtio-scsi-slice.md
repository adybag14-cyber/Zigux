# Phase 12 Virtio SCSI Slice

This bounded Phase 12 slice adds the first Zigux `virtio scsi` starter anchored to `drivers/scsi/virtio_scsi.c`.

The starter stays intentionally narrow:

- plans the control, event, and request virtqueue family layout from the requested request-queue count and poll-queue hint
- preserves the Linux driver rule that poll queues are clamped so at least one default request queue remains
- classifies each planned request queue as either `request` or `request_poll` with stable global virtqueue indexes starting after the control and event queues
- records the fixed event-buffer fanout used by the driver without claiming event work handling, request submission, or live transport reset completion
- freezes queue planning and event recycling intent across a lab-only transport freeze or restore boundary, derives one restore-time queue reinitialization plan from the frozen control, event, default-request, and poll-request topology, then clears the old queue snapshot so the next step must replan instead of pretending virtqueues stayed live
- captures one probe snapshot of `virtscsi_probe()` config fields such as `num_queues`, `seg_max`, `cmd_per_lun`, `max_target`, `max_lun`, and `max_sectors`, plus the derived control, event, default-request, and poll-request queue layout
- records one host-limit summary that clamps `cmd_per_lun` against a synthetic `can_queue` and captures the derived `max_target`, `max_lun`, `max_sectors`, and `nr_hw_queues` values before any `Scsi_Host` registration work

This slice does not claim DMA mapping, scatter-gather command assembly, `Scsi_Host` registration, blk-mq submission, event-work recycling, TMF handling, hotplug, or live transport reset recovery.

The next honest bounded step inside the same Phase 12 lane is now to keep the lane parked on survey or validation evidence until the roadmap-approved queue ownership, SCSI-host lifecycle, and DMA-backed transport substrate exists for a real runtime follow-up.
