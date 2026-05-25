# Phase 12 NVMe PCI Slice

This driver-local slice keeps the current `nvme_pci` packet bounded to queue-pair planning, IO queue reservation sizing, recovery reservation replay debt, preflight and applied summaries, queue-numbering restart review, PRP span accounting, PRP metadata budgeting, stale PRP metadata ownership and descriptor-rebuild governance, reset-freeze summaries, dropped-backlog retirement review, rollback-gate review, and frozen queue-restore budgeting.

It stays below live DMA mapping, PRP or SGL construction, blk-mq submission, interrupt completion, timeout recovery, and transport-backed reset replay.