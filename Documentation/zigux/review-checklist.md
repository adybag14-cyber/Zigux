# Zigux Review Checklist

Use this checklist before opening or merging Zigux product work.

## Scope
- is the target phase named explicitly?
- is the status bucket explicit: port now, port after substrate, dual implementation required, study only, or freeze in C initially?
- is the Linux anchor file or tree path named directly?

## Safety
- does the change avoid mirror-tree sprawl?
- is real code co-located with the owning Linux subsystem when appropriate?
- does the change avoid deep-core scope creep into scheduler, MM, RCU, or skbuff without an Architecture Council decision?

## Validation
- are parity tests or fixture checks included?
- is there a stated performance gate if the code is algorithmic, queueing-sensitive, or driver-facing?
- is there a stated rollback owner and fallback path?
- if the change is a reference sample under `samples/zigux/`, is the self-check or behavior replay explicit and small enough to stay reviewable?
- if the change updates an existing Phase 5 sample, do the descriptor, manifest-backed survey, sample-backed survey note, and shared `phase5_build.zig` entrypoint still agree on the same Linux anchor and exact replay contract?
- if the change updates a landed Phase 5 sample that keeps a Linux concurrency or private-data cue only for reviewability, does the note or checklist still say clearly what remains in-memory-only and what runtime parity is still out of scope?
- if the change is a Phase 9 runtime slice, do the module or sample note, the manifest-backed survey or loader-gap survey, and the shared `phase9_build.zig` entrypoint still agree on the same Linux anchor, bounded blocker posture, and replay scope?
- if the change touches the shared Phase 9 runtime-loader evidence packet, does the manifest-backed catalog and ownership map still keep the survey note, review checklist, shared request contract, sample-side loader plans, and `phase9_build.zig` entrypoint in one reviewable ownership packet?
- if the change touches the shared Phase 9 runtime-loader handoff, are allocator ownership, `requires_runtime_substrate`, handoff stage, and the still-blocked command-name, argv-policy, or environment-derived activation controls explicit rather than implied?
- if a Phase 9 runtime trace-events change touches the frozen trace-core boundary, do `Documentation/zigux/freeze-map.md`, the trace-events docs, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` still keep `kernel/trace/ring_buffer.c` as `Study / Boundary Only` and require an Architecture Council decision before any status change?
- if the change is a Phase 10 virtio slice, do `Documentation/zigux/phase10-closure-evidence.md`, its roadmap parity scoreboard, `zigux/tests/phase10_closure_manifest.json`, the four Phase 10 survey manifests, the landed `Documentation/zigux/phase10-virtio-mmio-slice.md` plus `zigux/tests/phase10_virtio_mmio.zig` starter pair, and the shared `zigux/tests/phase10_build.zig` entrypoint still agree on the same bounded lab-only scope, exact replay commands, and explicit MMIO blocker posture?
- if the change touches the Phase 10 scoreboard or closure packet, do the Phase 5 sample lane and Phase 9 runtime lane still stay outside the Phase 10 virtio parity readout so `samples/zigux/`, `zigux/tests/phase5_build.zig`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `zigux/tests/phase9_build.zig` are not silently counted as driver-local virtio evidence?
- if the change widens a Phase 10 virtio transport-facing path, do `Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-closure-evidence.md`, and the ring/input/MMIO survey manifests still keep the risky transport posture explicit instead of silently widening MMIO, queue setup or reset, IRQ, registration, DMA, or probe/remove lifecycle claims?
- if the change is a Phase 11 simple-driver slice, do `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, the four driver-local Phase 11 manifests, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still agree on the same bounded simple-driver scope, shared replay contract, and explicit ready-next versus blocked follow-up posture?
- if the change touches the shared Phase 11 tooling path, do `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `zigux/tests/phase11_hvc_console_survey.zig` still agree on the exact shared build inventory and the dedicated-survey boundary instead of silently implying that every Phase 11 survey gate already runs in the shared path?
- if the change is a Phase 12 complex-driver or heavy-helper slice, do `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, and the four Phase 12 manifests still agree on the same bounded tranche, approved roadmap destinations, shared replay contract, and explicit DMA versus object-model blocker posture?
- if the change touches the shared Phase 12 degraded-workflow packet, do the workflow path, README notes, review checklist, and `zigux/tests/phase12_virtio_scsi_survey.zig` still agree that `make -C zigux phase12` runs the validator before the shared Zig replay?
- if the change touches a freeze-map anchor, is the parity scorecard evidence or blocker state explicit?
- if the change asks for a freeze-map status change, is the Architecture Council review record linked and are the current status bucket plus requested decision bucket explicit?
- if a freeze-map anchor is entering Architecture Council status review, are the decision record ID, lane owner, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, and replay command explicit?
- if a freeze-map anchor is closing review with a stay-in-C outcome, are the retained discussion state and reopen triggers explicit?
- if a freeze-map anchor remains blocked, does the scorecard still name the current lane owner responsible for keeping that blocked evidence packet up to date?

## ABI and Runtime
- are bindings and ABI assumptions centralized?
- does the change avoid hidden runtime services, implicit allocation, or unclear panic behavior?
- if unsafe code exists, is it narrow, visible, and review-owned?

## Product Discipline
- does the patch make Zigux more buildable, more testable, or more reviewable?
- if it came from ZAR research, is the transfer rationale explicit?
- if the target stays in C, does the change record that ongoing policy honestly instead of implying a premature port commitment?
- does the change strengthen the product repo instead of just extending experimental scope?
- if the change is a Phase 5 sample, does it separate reviewable idiom guidance from later runtime-substrate claims such as procfs, user-copy, or module registration parity?
- if the change is a landed Phase 5 sample, does it update the directly coupled survey note or manifest-backed contributor prompts when the sample contract changes?
