# Phase 14 Attached Toolchain Guidance Gap

## Scope
- lane: `P14-L07`
- phase: `Phase 14`
- packet: shared validator-plus-guidance packet for the bounded Phase 14 smoke route
- status: `current-master gap`

## Why this note exists
The Phase 14 roadmap keeps the shared smoke packet in a study-only, reviewability-first posture. That means the shipped guidance needs to stay explicit about how reviewers rerun the bounded smoke route when the attached Zig toolchain is the only available compiler instead of leaving that fallback visible only in one packet-local note.

## Current repo readback
The current `Documentation/zigux/phase14-end-to-end-smoke-survey.md` packet already carries attached-toolchain fallback examples for the shipped Phase 14 smoke routes:
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`
- `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`

The current scripts-root reminder does not carry the same attached-toolchain fallback guidance in its Phase 14 block. It names the shipped `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, `make -C zigux phase14`, and shared build routes, but it stops short of telling reviewers how to rerun the same bounded packet when `zig` is unavailable on `PATH`.

The dedicated shared smoke survey gate also still checks only the basic scripts-root markers around `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and the focused smoke-shard replay contract. The shared validator packet likewise does not currently fail closed on an attached-toolchain fallback marker in the scripts-root reminder.

## Why this matters
This is a real operational gap rather than a new delivery claim:
- the roadmap says Phase 14 stays bounded, study-only, and reviewability-first
- the bootstrap ledger favors exact rerun guidance over implied routes
- the attached toolchain is already part of the operating environment for bounded Zig validation
- the current shared guidance packet leaves the fallback route discoverable from the Phase 14 smoke note but not from the scripts-root reminder that contributors are expected to consult first

## Smallest honest same-lane repair
The next bounded `P14-L07` repair should stay inside the shared validator-plus-guidance packet only:
1. add one scripts-root Phase 14 reminder line that mirrors the attached-toolchain fallback already documented in `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
2. extend `zigux/tests/phase14_end_to_end_smoke_survey.zig` so the shared smoke survey fails if that scripts-root fallback wording disappears
3. extend `scripts/zigux/validate-phase14.py` only if needed so the shared validator packet also fails closed on the same scripts-root fallback marker

## Non-goals
- do not reopen workqueue, ring-buffer, skbuff, or RCU packet contents
- do not introduce a new Phase 14 replay route
- do not imply any live deep-core execution ownership or status change
- do not widen into Phase 15 freeze-map governance
