# Phase 12 Virtio SCSI Slice

This bounded Phase 12 slice adds the first Zigux `virtio scsi` starter anchored to `drivers/scsi/virtio_scsi.c`.

The starter stays intentionally narrow:

- plans the control, event, and request virtqueue family layout from the requested request-queue count and poll-queue hint
- preserves the Linux driver rule that poll queues are clamped so at least one default request queue remains
- classifies each planned request queue as either `request` or `request_poll` with stable global virtqueue indexes starting after the control and event queues
- records the fixed event-buffer fanout used by the driver without claiming event work handling, request submission, or live transport reset completion
- freezes queue planning and event recycling intent across a lab-only transport freeze or restore boundary, derives one restore-time queue reinitialization plan from the frozen control, event, default-request, and poll-request topology, blocks queue-depth capture while transport is still frozen, then clears the old queue snapshot so the next step must replan instead of pretending virtqueues stayed live; the focused gate now also proves that a second freeze or restore cycle uses the newly replanned topology and increments the bounded recovery generation instead of reusing stale queue state
- the restore summary now makes post-reset governance explicit by marking queue layout replanning as required and by marking the cached probe, host-limit, queue-depth, and io-queue-map summaries as cleared, so the bounded packet does not imply that pre-reset queue ownership or cached capacity snapshots survive a restore
- captures one probe snapshot of `virtscsi_probe()` config fields such as `num_queues`, `seg_max`, `cmd_per_lun`, `max_target`, `max_lun`, and `max_sectors`, plus the derived control, event, default-request, and poll-request queue layout
- records one host-limit summary that clamps `cmd_per_lun` against a synthetic `can_queue` and captures the derived `max_target`, `max_lun`, `max_sectors`, and `nr_hw_queues` values before any `Scsi_Host` registration work
- records one queue-depth summary that reuses the bounded host-limit snapshot to mirror `virtscsi_change_queue_depth()`, clamping a requested depth against effective `cmd_per_lun` while keeping `track_queue_depth` reviewable before any live `Scsi_Host` registration work
- records one `io_queues` and blk-mq queue-map summary that keeps the bounded default, read, and poll queue counts plus their queue offsets in memory before any live `map_queues` callback, CPU-affinity wiring, or blk-mq submission path is attempted
- derives one recovery-time blk-mq queue-map restore summary from the frozen queue layout so the bounded default, read, and poll map counts plus their offsets remain reviewable across transport reset without claiming a live `map_queues` callback or CPU-affinity restore
- derives one bounded restore-sequencing summary from the frozen queue layout so the starter now records `virtscsi_restore()` re-entering `virtscsi_init()`, requiring `find_vqs` before `virtio_device_ready()`, and only rearming event buffers with `virtscsi_kick_event_all()` after the device-ready step while still making it explicit that the restore helper does not pretend to re-run `scsi_scan_host()` or port live `Scsi_Host` registration

This slice does not claim DMA mapping, scatter-gather command assembly, `Scsi_Host` registration, blk-mq submission, event-work recycling, TMF handling, hotplug, or live transport reset recovery beyond the bounded queue, map, and restore-sequencing summaries above.

The next honest bounded step inside the same Phase 12 lane is now to keep the lane parked on survey or validation evidence until the roadmap-approved queue ownership, SCSI-host lifecycle, and DMA-backed transport substrate exists for a real runtime follow-up beyond the current queue-layout, recovery, restore-sequencing, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters.
