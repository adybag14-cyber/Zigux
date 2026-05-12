# Phase 5 Kretprobe Sample Next-Step Note

This note records one bounded follow-through step for the landed Phase 5 `samples/zigux/kretprobe_example.zig` packet.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_LANE_KEY=P5-Y06`
- `PHASE5_SLICE=kretprobe-sample-next-safe-step-note`
- scope: sample-only review-surface truthfulness for the landed non-runtime kretprobe packet

## Current repo evidence

Fresh repo evidence shows that the live kretprobe sample packet already agrees on the split replay surface:

- `samples/zigux/kretprobe_example.zig` exposes `runAnchorReplay()`, `runRetargetReplay()`, `runOwnershipReplay()`, `runRecoveryReplay()`, and `runLifecycleGuardReplay()`.
- `samples/zigux/kretprobe_example.zig` keeps the fixed review-only `maxactiveBudget()` cue at `20`.
- `zigux/tests/phase5_kretprobe_example_manifest.json` describes the same split replay contract for pre-init retargeting, ownership snapshots, recovery, lifecycle guards, the fixed budget cue, and the missed-instance summary.

The current packet-local drift is in shared wording, not in sample behavior:

- `samples/zigux/README.md` still names stale combined helpers `runRetargetRecoveryReplay()`, `runMaxactiveBudgetReplay()`, and `runOwnershipBoundaryReplay()` for this sample.
- `Documentation/zigux/phase5-sample-review-guide.md` still repeats those same stale combined helper names for the kretprobe packet.

## One bounded next safe step

Apply one wording-only repair to the `samples/zigux/README.md` kretprobe paragraph so it names the live sample-owned replay helpers exactly as shipped:

- `runRetargetReplay()`
- `runOwnershipReplay()`
- `runRecoveryReplay()`
- `runLifecycleGuardReplay()`
- `maxactiveBudget()`

Keep that repair limited to the kretprobe paragraph only. Do not change sample code, the manifest, the dedicated survey note, the focused Phase 5 test entrypoint, or the separate Phase 9 `runtime_kretprobe` packet in the same step.

## Why this is the safest next move

The sample code and manifest already agree on the exact contract, so the smallest honest follow-through is to narrow one stale shared reminder surface back to that shipped packet instead of reopening sample semantics or widening into cross-sample guide cleanup.

## Non-goals

This note does not reopen:

- sample behavior in `samples/zigux/kretprobe_example.zig`
- the dedicated survey note or manifest contract
- runtime `kretprobe` starter or loader work
- broad multi-sample Phase 5 guide cleanup beyond this sample's exact helper names
