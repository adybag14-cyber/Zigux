# Phase 14 ZAR Runtime Research Absorption

This note records the bounded P14-L06 absorption of ZAR runtime research into the Phase 14 core-adjacent boundary packet. It is intentionally notes-only: the useful output is review vocabulary for existing Phase 14 study and freeze surfaces, not a new Zig bridge, route, or parity claim.

## Status

- `PHASE14_LANE_KEY=P14-L06`
- `PHASE14_PHASE=Phase 14`
- `PHASE14_SLICE=zar-runtime-research-absorption`
- `PHASE14_POSTURE=study_only_discipline_transfer`
- `PHASE14_STATUS_CHANGE_CLAIM=no`
- `PHASE14_SOURCE=ZAR-Zig-Agent-Runtime-main/docs/architecture.md`
- refreshed against the current Phase 14 packet and the attached `ZAR-Zig-Agent-Runtime-main (11).zip` archive on `2026-05-29`
- additional source context read: `ZAR-Zig-Agent-Runtime-main/docs/memory-edge.md`, `ZAR-Zig-Agent-Runtime-main/docs/security-and-diagnostics.md`, `ZAR-Zig-Agent-Runtime-main/README.md`, `ZAR-Zig-Agent-Runtime-main/docs/zig-port/PHASE_CHECKLIST.md`, and `ZAR-Zig-Agent-Runtime-main/docs/zig-port/PORT_PLAN.md`
- role: absorb reusable reviewability discipline from ZAR runtime research into the roadmap-backed Phase 14 note family without turning that research into bridge promotion, replay closure, or a freeze-map status-change claim

## Why this note exists

The Phase 14 roadmap keeps `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c` in a bounded study-only or freeze-in-C posture.

Current `master` already carries shared-smoke truthfulness notes, workqueue reviewability surfaces, a ring-buffer survey companion, a skbuff stay-in-C survey, an RCU freeze-in-C survey, and Phase 15 study-only accounting. The useful same-lane work is therefore not another bridge. It is a disciplined explanation of which parts of the attached ZAR runtime research are safe to absorb into those Phase 14 notes.

This note fills that smaller gap. It is a discipline-transfer note, not a delivery packet.

## Research signals worth absorbing

### 1. Queue-drain evidence should be explicit and bounded

The archive's scheduler research repeatedly proves narrow queue-drain seams instead of claiming a full scheduler replacement:

- `ZAR-Zig-Agent-Runtime-main/README.md` records `submitCommandSync(...)`-based scheduler-owned AP dispatch and later fairness-drain slices
- `ZAR-Zig-Agent-Runtime-main/docs/zig-port/PHASE_CHECKLIST.md` records bounded scheduler-window and fairness-drain proofs with cumulative counters, pending-task visibility, and explicit broader-scheduler gaps
- `ZAR-Zig-Agent-Runtime-main/docs/zig-port/PORT_PLAN.md` keeps the same progression explicit through fairness, rebalance, debt, admission, and aging probes

The reusable lesson for Zigux is not the AP scheduler code shape. The reusable lesson is that queue-drain research stays honest when it publishes bounded counters, remaining-work visibility, cursor or round telemetry, and an explicit statement of what still remains outside the proven seam.

### 2. Reset and lifecycle proofs belong beside the seam they bound

The archive also keeps lifecycle and reset behavior explicit rather than implying it from bridge presence alone:

- `ZAR-Zig-Agent-Runtime-main/docs/operations.md` records bounded teardown, timeout, and smoke-check behavior for runtime operations
- `ZAR-Zig-Agent-Runtime-main/docs/architecture.md` says runtime instances are initialized on demand and reset on config changes
- `ZAR-Zig-Agent-Runtime-main/docs/security-and-diagnostics.md` keeps remediation behavior explicit through structured fix results and unresolved manual-action reporting

The reusable lesson for Zigux is that teardown, reset, and lifecycle ownership need their own named review surfaces. That maps directly onto the existing Phase 14 stay-in-C seams around flush or drain progression, cancellation completion, destructor ordering, queue publication, and callback ownership.

### 3. Handoff and wakeup claims should stay narrower than bridge presence

The archive's SMP and runtime work keeps handoff evidence explicit through warm-reset programming, AP startup observation, scheduler-owned mailboxes, bounded fairness or rebalance probes, and still-open broader scheduling gaps.

That matters for Phase 14 because the risky surfaces around workqueue, ring buffer, skbuff, and RCU are all handoff-heavy:

- workqueue: manager-role serialization, delayed-work requeue, callback dispatch, rescuer coordination, and hotplug rebinding
- ring buffer: reader-page handoff, wakeup publication, mapped-reader teardown, and resize or splice lockout behavior
- skbuff: publication, checksum ownership, destructor ordering, and final tail transfer
- RCU tree: grace-period publication, callback wakeups, quiescent-state propagation, and hotplug callback migration

The reusable lesson is simple: handoff-heavy surfaces need named blocker wording and explicit proof boundaries even when a bridge, manifest, or survey note is already present.

### 4. Runtime layering can improve review language without becoming a port source

The 2026-05-29 refresh adds one narrower architecture lesson from the ZAR runtime docs:

gateway and dispatcher layering maps only to review-boundary vocabulary. ZAR's protocol, gateway, dispatcher, and domain-service split is useful as a reminder to keep Phase 14 Linux anchors separated by contract boundary, policy ownership, and state handoff rather than by filename enthusiasm.

bounded in-memory histories and compact retention map only to audit prompts for workqueue and ring-buffer study notes. ZAR's memory and edge notes describe retained histories, compact lists, and diagnostic event surfaces; for Zigux Phase 14, those are review prompts for queue growth, flush/drain boundaries, trace event reader state, and ring-buffer publication ownership, not evidence that kernel workqueue or ring-buffer execution can move to Zig.

secret-store fallback reporting maps only to explicit stay-in-C and unsupported-backend wording. ZAR's machine-readable fallback states are a useful model for Phase 14 notes that must say when skbuff lifetime ownership, RCU grace-period ownership, scheduler-visible worker state, or trace-ring publication remains unsupported by Zigux.

bare-metal ABI lifecycle hooks map only to ABI-boundary review prompts. ZAR's exported lifecycle and mailbox hooks are useful vocabulary for Phase 14 bridge manifests that need explicit ABI ingress, rollback owner, and lifecycle reset wording, while the live Linux ownership stays in C unless the existing governance gates change.

## What Zigux should absorb from that research

Read this as a Phase 14 note-writing rule set, not as an implementation plan.

### Workqueue

Absorb the queue-drain discipline. Keep manager-role, forward-progress, pending-window, delayed-work, flush-drain, cancellation, rescuer, and hotplug wording explicit as bounded audit surfaces, and prefer backlog or drain-state accounting language over generic bridge-presence language.

### Ring buffer

Absorb the publication and teardown discipline. Keep reader handoff, wakeup publication, consume or extract serialization, mapped-reader teardown, compact-retention pressure, and resize lockout wording explicit as stay-in-C seams unless a future lane brings stronger dedicated evidence.

### Skbuff

Absorb the ownership and lifecycle discipline. Keep qdisc publication, checksum state, destructor ordering, segmentation metadata, unsupported ownership fallback, and final tail-transfer wording explicit as blocked ownership seams even when the bridge packet and build shard are readable.

### RCU tree

Absorb the handoff, reset, and ABI-boundary discipline. Keep grace-period publication, wakeup funnels, quiescent-state propagation, callback-barrier ownership, lifecycle reset claims, and hotplug migration wording explicit as freeze-in-C evidence rather than relaxing them into a generic survey summary.

## What Zigux should not absorb

- do not treat ZAR scheduler, gateway, dispatcher, memory, security, or transport code as a direct Phase 14 port source
- do not promote a bridge, manifest, shared-smoke route, or ZAR runtime pattern into parity or ownership evidence
- do not weaken the freeze-map split between study-only anchors and freeze-in-C anchors
- do not reopen `phase14-smoke`, `phase14-test`, or `phase14` wrapper claims from this note

## Phase 14 packet impact

This note sharpens the meaning of the existing Phase 14 packet without changing its status:

- it supports `Documentation/zigux/phase14-core-boundary-traceability.md` by making the transferable research discipline explicit
- it supports `Documentation/zigux/phase14-workqueue-bridge-survey.md`, `Documentation/zigux/phase14-ring-buffer-survey.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, and `Documentation/zigux/phase14-rcu-tree-survey.md` by reinforcing why research lessons and bridge presence stay below live ownership
- it supports `Documentation/zigux/phase14-end-to-end-smoke-survey.md` and `Documentation/zigux/phase14-release-boundary-survey.md` by keeping research absorption in the reviewability lane rather than turning it into replay inflation
- it stays aligned with `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` by preserving the current study-only versus freeze-in-C split

## Validation surface

The bounded checker for this note is `scripts/zigux/check-phase14-zar-runtime-research-absorption.py`. It fail-closes on the source marker, the four refreshed runtime lessons, the no-new-bridge posture, and forbidden parity or ownership claims.

## Non-goals

This note does not claim:

- a new bridge file
- a new Makefile route
- a returned executable-layer readback
- a Phase 14 ownership transfer
- a Phase 15 governance status change

It also does not add `kernel/workqueue_bridge.zig`, `kernel/trace/ring_buffer.zig`, `net/core/skbuff_bridge.zig`, or `kernel/rcu/tree_bridge.zig`, and it does not change the freeze map, Architecture Council posture, or Phase 15 governance packet.

## Next bounded step

If a future Phase 14 shared note or anchor-local survey needs a truthfulness refresh, borrow only the discipline captured here:

- publish bounded drain, reset, teardown, handoff, fallback, and ABI-boundary evidence explicitly
- keep broader gaps named beside the narrower proof
- keep study-only and freeze-in-C posture unchanged unless a dedicated governance lane lands stronger evidence

Until then, keep this note parked as a roadmap-aligned research-absorption companion rather than widening it into another shared-smoke packet owner.
