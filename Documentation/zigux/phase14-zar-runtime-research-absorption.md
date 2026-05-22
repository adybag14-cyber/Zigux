# Phase 14 ZAR Runtime Research Absorption

## Status
- `PHASE14_LANE_KEY=P14-L06`
- `PHASE14_PHASE=Phase 14`
- `PHASE14_SLICE=zar-runtime-research-absorption`
- `PHASE14_POSTURE=study_only_discipline_transfer`
- `PHASE14_STATUS_CHANGE_CLAIM=no`
- refreshed against the current Phase 14 packet and the attached `ZAR-Zig-Agent-Runtime-main (11).zip` archive on `2026-05-22`
- role: absorb reusable reviewability discipline from ZAR runtime research into the roadmap-backed Phase 14 note family without turning that research into a bridge-promotion, replay-closure, or freeze-map status-change claim

## Why this note exists
The Phase 14 roadmap keeps `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c` in a bounded study-only or freeze-in-C posture.

That same roadmap also says ZAR should feed Zigux only where it reduces product risk or hardens validation discipline. For Phase 14 specifically, the roadmap already treats bare-metal SMP work as research input rather than as a direct product port.

The current Zigux repo already carries shared-smoke truthfulness notes, workqueue reviewability surfaces, a ring-buffer survey companion, a skbuff stay-in-C survey, and Phase 15 study-only accounting. What it did not carry yet was one bounded note explaining which parts of the attached ZAR runtime research are actually worth absorbing into those Phase 14 notes.

This note fills that smaller gap. It is a discipline-transfer note, not a new delivery packet.

## Research signals worth absorbing
The attached ZAR runtime archive now carries several concrete patterns that are relevant to Phase 14 reviewability even though they do not justify a direct Zigux port.

### 1. Queue-drain evidence should be explicit and bounded
The archive's scheduler research repeatedly proves narrow queue-drain seams instead of claiming a full scheduler replacement:

- `ZAR-Zig-Agent-Runtime-main/README.md` records `submitCommandSync(...)`-based scheduler-owned AP dispatch and later fairness-drain slices
- `ZAR-Zig-Agent-Runtime-main/docs/zig-port/PHASE_CHECKLIST.md` records bounded scheduler-window and fairness-drain proofs with cumulative counters, pending-task visibility, and an explicit note that broader scheduling still remains outside the delivered seam
- `ZAR-Zig-Agent-Runtime-main/docs/zig-port/PORT_PLAN.md` keeps the same progression explicit through fairness, rebalance, debt, admission, and aging probes

The reusable lesson for Zigux is not the AP scheduler code shape.
The reusable lesson is that queue-drain research stays honest when it publishes bounded counters, remaining-work visibility, cursor or round telemetry, and an explicit statement of what still remains outside the proven seam.

### 2. Reset and lifecycle proofs belong beside the seam they bound
The archive also keeps lifecycle and reset behavior explicit rather than implying it from bridge presence alone:

- `ZAR-Zig-Agent-Runtime-main/docs/operations.md` records a bounded four-way TCP teardown state machine with explicit retransmission and timeout behavior
- `ZAR-Zig-Agent-Runtime-main/docs/architecture.md` says runtime instances are initialized on demand and reset on config changes
- `ZAR-Zig-Agent-Runtime-main/README.md` and `ZAR-Zig-Agent-Runtime-main/docs/operations.md` keep lifecycle smoke checks explicit for secret-store and trust-store flows instead of treating broader runtime presence as enough proof

The reusable lesson for Zigux is that teardown, reset, and lifecycle ownership need their own named review surfaces.
That maps directly onto the existing Phase 14 stay-in-C seams around flush or drain progression, cancellation completion, destructor ordering, queue publication, and callback ownership.

### 3. Handoff and wakeup claims should stay narrower than bridge presence
The archive's SMP work keeps handoff evidence explicit through warm-reset programming, AP startup observation, scheduler-owned mailboxes, and bounded fairness or rebalance probes, while still recording the broader scheduling gap instead of claiming completion.

That matters for Phase 14 because the risky surfaces around workqueue, ring buffer, skbuff, and RCU are all handoff-heavy:

- workqueue: manager-role serialization, delayed-work requeue, callback dispatch, rescuer coordination, and hotplug rebinding
- ring buffer: reader-page handoff, wakeup publication, mapped-reader teardown, and resize or splice lockout behavior
- skbuff: publication, checksum ownership, destructor ordering, and final tail transfer
- RCU tree: grace-period publication, callback wakeups, quiescent-state propagation, and hotplug callback migration

The reusable lesson is simple: handoff-heavy surfaces need named blocker wording and explicit proof boundaries even when a bridge, manifest, or survey note is already present.

## What Zigux should absorb from that research
Read this as a Phase 14 note-writing rule set, not as an implementation plan.

### Workqueue
Absorb the queue-drain discipline.
Keep manager-role, forward-progress, pending-window, delayed-work, flush-drain, cancellation, rescuer, and hotplug wording explicit as bounded audit surfaces, and prefer backlog or drain-state accounting language over generic bridge-presence language.

### Ring buffer
Absorb the publication and teardown discipline.
Keep reader handoff, wakeup publication, consume or extract serialization, mapped-reader teardown, and resize lockout wording explicit as stay-in-C seams unless a future lane brings stronger dedicated evidence.

### Skbuff
Absorb the ownership and lifecycle discipline.
Keep qdisc publication, checksum state, destructor ordering, segmentation metadata, and final tail-transfer wording explicit as blocked ownership seams even when the bridge packet and build shard are readable.

### RCU tree
Absorb the handoff and reset discipline.
Keep grace-period publication, wakeup funnels, quiescent-state propagation, callback-barrier ownership, and hotplug migration wording explicit as freeze-in-C evidence rather than relaxing them into a generic survey summary.

## What Zigux should not absorb
- do not treat ZAR scheduler or transport code as a direct Phase 14 port source
- do not promote a bridge, manifest, or shared-smoke route into parity or ownership evidence just because ZAR proved a bounded seam in another runtime
- do not weaken the freeze-map split between study-only anchors and freeze-in-C anchors
- do not reopen `phase14-smoke`, `phase14-test`, or `phase14` wrapper claims from this note

## Phase 14 packet impact
This note sharpens the meaning of the existing Phase 14 packet without changing its status:

- it supports `Documentation/zigux/phase14-core-boundary-traceability.md` by making the transferable research discipline explicit
- it supports `Documentation/zigux/phase14-workqueue-bridge-survey.md` and `Documentation/zigux/phase14-skbuff-bridge-survey.md` by reinforcing why bridge presence stays below live ownership
- it supports `Documentation/zigux/phase14-end-to-end-smoke-survey.md` and `Documentation/zigux/phase14-release-boundary-survey.md` by keeping research absorption in the reviewability lane rather than turning it into replay inflation
- it stays aligned with `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` by preserving the current study-only versus freeze-in-C split

## Non-goals
This note does not claim:
- a new bridge file
- a new Makefile route
- a returned executable-layer readback
- a Phase 14 ownership transfer
- a Phase 15 governance status change

## Next bounded step
If a future Phase 14 shared note or anchor-local survey needs a truthfulness refresh, borrow only the discipline captured here:

- publish bounded drain, reset, teardown, and handoff evidence explicitly
- keep broader gaps named beside the narrower proof
- keep study-only and freeze-in-C posture unchanged unless a dedicated governance lane lands stronger evidence

Until then, keep this note parked as a roadmap-aligned research-absorption companion rather than widening it into another shared-smoke packet owner.