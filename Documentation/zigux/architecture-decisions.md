# Zigux Architecture Council Decisions

This index keeps the Architecture Council decision surface reviewable from one stable page.

It does not replace the freeze map or the dedicated Phase 15 governance notes. It exists so future status reviews, stay-in-C closeouts, and approved status-bucket changes have one durable registry instead of being inferred from scattered reminder documents.

## Current posture

- current reviewable status-change approvals recorded on `master`: none
- current stay-in-C closeout records recorded on `master`: none
- current Architecture Council review packets that are decision-shape ready on `master`: none
- current deep-core posture: keep `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` in `freeze_in_c`
- current study-only posture: keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` as study-only anchors outside freeze-in-C status review

The current truthful governance state is therefore blocker accounting plus review-packet preparation, not an approved status change.

## Source documents

Read these documents together before adding or updating a decision record:

- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-architecture-council-decision-record-template.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- `Documentation/zigux/review-checklist.md`

## Record classes

Keep future entries in one of these bounded classes:

### Approved status-bucket changes

Use for a published Architecture Council decision that moves a freeze-in-C anchor into a different allowed bucket.

Requirements:

- linked decision record ID
- exact Linux anchor path
- required approver set
- parity scorecard entry
- evidence archive path
- rollback owner
- replay command
- next bounded follow-up step

### Stay-in-C closeouts

Use for a published closeout that keeps an anchor in `freeze_in_c`.

Requirements:

- linked decision record ID
- retained blocker
- `retired_from_active_discussion` state
- automatic return-to-blocked trigger
- reopen triggers
- trigger-specific evidence refresh
- evidence archive path
- next bounded follow-up step

### Blocked review packets

Use only when a repo-local document becomes a stable, reviewable packet that is ready to be tracked as an explicit Architecture Council request.

Requirements:

- linked review packet path
- current status bucket
- requested decision bucket
- blocker disposition
- evidence archive path
- owner
- next bounded step

Do not add study-only anchors here unless the freeze map itself changes first.

## Decision record naming

Use stable IDs shaped like:

- `AC-YYYYMMDD-<anchor-short-name>`

Examples:

- `AC-20260527-kernel-rcu-tree`
- `AC-20260527-net-core-skbuff`

If no reviewable record exists yet, do not reserve an ID just to make the registry look active.

## Evidence archive map

The current freeze-in-C evidence archive paths are:

- `kernel/sched/core.c` -> `Documentation/zigux/phase15-evidence-archives/kernel-sched-core.md`
- `mm/page_alloc.c` -> `Documentation/zigux/phase15-evidence-archives/mm-page-alloc.md`
- `kernel/rcu/tree.c` -> `Documentation/zigux/phase15-evidence-archives/kernel-rcu-tree.md`
- `net/core/skbuff.c` -> `Documentation/zigux/phase15-evidence-archives/net-core-skbuff.md`

These archive paths belong with the governing Phase 15 packet and should stay aligned with `Documentation/zigux/phase15-freeze-map-governance.md`.

## Active registry

### Approved status-bucket changes

None recorded on current `master`.

### Stay-in-C closeouts

None recorded on current `master`.

### Blocked review packets

None recorded on current `master`.

The current repo state keeps the review process and template landed, but it does not yet carry a published Architecture Council record for any freeze-map anchor.

## Maintenance rules

- update this index only when a real Architecture Council record lands or an existing record changes state
- keep this index aligned with the freeze map, the dedicated review-process note, and the dedicated decision-record template
- keep study-only anchors out of this registry unless the freeze map and supporting governance packet explicitly move them into review scope
- if a shared reminder surface claims an approved status change, that claim must also appear here with the linked decision record ID and evidence archive path

## Next bounded step

Keep this page parked until one of these events happens:

- a freeze-in-C anchor gets its first published Architecture Council decision record
- a stay-in-C closeout is published and needs a durable registry entry
- a broader reminder surface starts implying a decision exists without a matching registry entry here
