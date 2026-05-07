# Phase 5 Sample Lane Sequencing

This note keeps the shipped Phase 5 reference-sample packet reviewable without letting nearby sample lanes reopen the same packet from different shared surfaces at once.

Use it when a scheduled run touches the shared Phase 5 sample packet and needs to decide whether the work belongs in a shared guidance surface or in one sample-owned packet.

## Why this note exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" for four Linux anchors only:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Current `master` already ships all four bounded `samples/zigux/` reference readings plus one shared Phase 5 review packet.

The current overlap risk is no longer "which sample is missing." It is shared-surface drift: docs-root, sample-root, tests-root, checklist, and shared build-route wording can all mention the same four-sample packet even though the packet-local truth still belongs to one owning sample lane at a time.

## Shared routing surfaces only

Treat these as shared routing or contributor-guidance surfaces, not as the owner of packet-local sample semantics:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_build.zig`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

These shared surfaces may summarize the packet, replay it, or route contributors toward it.
They do not own:

- per-sample replay names
- per-sample manifest review prompts
- per-sample survey-note truthfulness
- sample-local non-goals
- sample-local exact check wording

If one of these shared surfaces drifts, repair only the wording or route needed to reflect the already-owned sample packet. Do not treat that drift as permission to reopen sample behavior or packet-local semantics.

## Sample-owning lanes

### `bytestream_fifo`

Owning lane
- `P5-L01`

Owned packet
- `samples/zigux/bytestream_fifo.zig`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `zigux/tests/phase5_bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_manifest.json`
- `zigux/tests/phase5_bytestream_fifo_survey.zig`

Packet-local follow-through belongs here when the drift is about queue-order replay, preview or snapshot behavior, queue-shape cues, helper-boundary wording, lifecycle wording, or sample-local non-goals.

### `kobject_example`

Owning lane
- `P5-Y03`

Owned packet
- `samples/zigux/kobject_example.zig`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`
- `zigux/tests/phase5_kobject_example_survey.zig`

Packet-local follow-through belongs here when the drift is about registration boundaries, `ownershipSummary()`, `runPreRegistrationBoundaryReplay()`, `runRegisteredBoundaryReplay()`, `runOwnershipReplay()`, `runTeardownReplay()`, attribute-group wording, or sample-local non-goals.

### `kretprobe_example`

Owning lane
- `P5-L18`

Owned packet
- `samples/zigux/kretprobe_example.zig`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`

Packet-local follow-through belongs here when the drift is about retargeting, `runLifecycleGuardReplay()`, `runRecoveryReplay()`, `ownershipSummary()`, private-data wording, missed-instance wording, teardown rejection, or sample-local non-goals.

### `trace_events_sample`

Owning lane
- `P5-L16`

Owned packet
- `samples/zigux/trace_events_sample.zig`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Packet-local follow-through belongs here when the drift is about `formattedMessage()`, `runPayloadBoundaryReplay()`, `runCallbackBoundaryReplay()`, `checked_focus` ordering, callback-balance wording, manifest review prompts, post-exit rejection, or sample-local non-goals.

## Routing rules

1. If the proposed edit changes a sample file, its survey note, its manifest, or its paired survey test, route the work to that sample's owning lane first.
2. If the proposed edit changes only a shared summary, checklist line, review guide, or replay route, keep the work in a shared surface and reflect only what the owning sample packet already says.
3. If the proposed edit starts to touch `samples/zigux/runtime_*`, `zigux/kernel/runtime_loader.zig`, or `zigux/tests/phase9_build.zig`, stop and route the work to the separate Phase 9 runtime pilot family instead of expanding Phase 5.
4. If a shared surface seems to require a packet-local fix, narrow the run to the smallest owner-confirming readback first, then move the packet-local repair into the owning sample lane rather than mixing both scopes casually.
5. Keep the shipped replay routes explicit as shared routes only: `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, `make -C zigux phase5-test`, and `make -C zigux phase5` rerun the packet but do not decide ownership by themselves.
6. Do not invent a shared `validate-phase5.py`, `check-phase5-*.py`, or `phase5-validate` owner surface unless one actually lands on `master` first.

## Anti-overlap reminders

- The shared Phase 5 packet is four samples only.
- There is still no standalone Phase 5 `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample on current `master`.
- Direct helper reviewability for those families stays with their own phases, and the separate `runtime_bitmap`, `runtime_trace_events`, and `runtime_kretprobe` surfaces stay Phase 9 work.
- A shared-surface note should never be used to reopen sample semantics just because it is easier to edit than the owning packet.

## Next-step rule

If a future scheduled run reopens this note, keep the follow-through limited to one shared-surface routing repair that makes the owning sample lane easier to identify. Any packet-local semantic or manifest change should move back into the owning sample lane instead of growing this shared sequencing note.