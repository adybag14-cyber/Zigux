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
- if the change updates an existing Phase 5 sample, do the descriptor, manifest, and shared `phase5_build.zig` entrypoint still agree on the same Linux anchor and exact replay contract?
- if the change updates a landed Phase 5 sample that keeps a Linux concurrency or private-data cue only for reviewability, does the note or checklist still say clearly what remains in-memory-only and what runtime parity is still out of scope?
- if the change touches a freeze-map anchor, is the parity scorecard evidence or blocker state explicit?
- if the change asks for a freeze-map status change, is the Architecture Council review record linked and are the current status bucket plus requested decision bucket explicit?
- if a freeze-map anchor is entering Architecture Council status review, are the decision record ID, lane owner, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, and replay command explicit?
- if a freeze-map anchor is closing review with a stay-in-C outcome, are the retained discussion state and reopen triggers explicit?
- if a freeze-map anchor remains blocked, does the scorecard still name the current lane owner responsible for keeping that blocked evidence packet up to date?
- if the change touches the shared Phase 14 smoke packet, do the four anchor-local manifests, the shared smoke and release-boundary surveys, the freeze map, and the `make -C zigux phase14` / `make -C zigux phase14-smoke` replay contract still agree on the same study-only stay-in-C posture?

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
