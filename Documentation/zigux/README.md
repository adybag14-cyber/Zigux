# Zigux Documentation

This directory is the product documentation root for Zigux.

Scope
- product charter
- review rules
- freeze map
- phase closure records
- phase policy
- future porting guides
- validation and artifact-diff policy

Rules
- keep product commitments here, not in ad hoc issue threads
- keep deep-core freeze decisions explicit
- require validation and rollback language for every new active port target
- align all new product docs with `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`

Current closure records
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase2-closure.md`

Phase 2 notes
- `python3 scripts/zigux/artifact_diff.py --self-test` is now part of the published Phase 2 closure path through `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/artifact-diff.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, so shared comparison drift fails before the bounded host-tool parity lanes run.

Phase 5 notes
- `Documentation/zigux/phase5-kfifo-sample-survey.md` now records the landed `samples/zigux/bytestream_fifo.zig` reference sample, its exact replay plus non-destructive snapshot checks, and the remaining non-goals around procfs, user-copy, and module registration parity.
- the same Phase 5 survey note now doubles as the sample-backed contributor guide for the landed bytestream FIFO slice by naming the descriptor, manifest, and shared build-entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kobject-sample-survey.md` now records the landed `samples/zigux/kobject_example.zig` reference sample, its exact registration, Linux `foo`/`baz`/`bar` attribute-order, and attribute-roundtrip checks, and the remaining non-goals around sysfs creation, `kernel_kobj`, uevents, and module registration.
- the same kobject survey note now doubles as the sample-backed contributor guide for the landed kobject slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kretprobe-sample-survey.md` now records the landed `samples/zigux/kretprobe_example.zig` reference sample, its exact skip, private-data-shape, return-value, duration, and `nmissed` replay checks, and the remaining non-goals around probe registration, `pt_regs`, and module wiring.
- the same kretprobe survey note now doubles as the sample-backed contributor guide for the landed non-runtime `kretprobe` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime starter.
- `Documentation/zigux/phase5-trace-events-sample-survey.md` now records the landed `samples/zigux/trace_events_sample.zig` reference sample, its exact payload, string-selection, formatted-message, event-family-count, vararg-payload, relative-location, callback-path, and callback-registration replay checks, and the remaining non-goals around tracepoint macros, kernel scheduling, and module wiring.
- the same trace-events survey note now doubles as the sample-backed contributor guide for the landed non-runtime `trace-events` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime pilot tranche.
- the Phase 5 notes now carry all four roadmap sample anchors as bounded `samples/zigux/` reference readings, while still keeping the separate Phase 9 runtime pilot tranche explicit for the same `trace-events` and `kretprobe` families.

Phase 4 notes
- `make -C zigux phase4-validate` runs `python3 scripts/zigux/artifact_diff.py --self-test` plus `python3 scripts/zigux/validate-phase4.py` before the shared Phase 4 Zig gate.
- `python3 scripts/zigux/validate-phase4.py` keeps the live `zigux/tests/runtime_atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` rollback gates wired through the shared `zigux/tests/phase4_build.zig` entrypoint and the bootstrap workflow.
- `Documentation/zigux/phase4-validation-matrix.md` records the current Phase 4 rollback owners, threshold posture, the exact bootstrap workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, the shared `phase4-runtime-atomic64-diff-tests` plus `phase4-bitmap-diff-tests` build entries that make local replay measurable, and the reversible-delivery evidence that ties each shipped gate back to its current C anchor if the shared Phase 4 entrypoint has to drop that Zig gate.

Phase 6 notes
- `Documentation/zigux/phase6-base64-slice.md`
- `Documentation/zigux/phase6-bsearch-slice.md`
- `Documentation/zigux/phase6-checksum-slice.md`
- `Documentation/zigux/phase6-hexdump-slice.md`
- `zigux/tests/phase6_build.zig` and `make -C zigux phase6` now gate the current base64, bsearch, checksum, and hexdump helper bundle together, so new helper slices should only land when that shared lane stays green as one unit.
- the current bounded Phase 6 decision is no longer whether the hexdump fixture wiring works in CI; it is whether the current bsearch, checksum, and hexdump parity evidence is sufficient to park the leaf-helper lane or whether one more tiny external fixture is still worth carrying.

Phase 7 notes
- `Documentation/zigux/phase7-string-helpers-slice.md`
- `Documentation/zigux/phase7-cmdline-slice.md`
- `Documentation/zigux/phase7-argv-split-slice.md`
- `Documentation/zigux/phase7-rbtree-slice.md`
- `zigux/tests/phase7_build.zig` and `make -C zigux phase7` now gate the current string-helpers, cmdline, argv-split, and rbtree helper bundle together, so Phase 7 helper work should stay reviewable through that shared lane instead of adding ad hoc per-slice CI steps.
- the Phase 7 helper bundle is now parked end-to-end: cmdline, argv-split, rbtree, and the bounded string-helpers slice all carry their current dedicated proofs through the shared `phase7_build.zig` gate, so future work here should reopen only for a concrete newly observed parity gap rather than for more speculative fixture expansion.

Phase 8 notes
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-help-slice.md`
- `Documentation/zigux/phase8-kallsyms-slice.md`
- `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`
- `Documentation/zigux/phase8-bpf-type-names-slice.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `zigux/tests/phase8_build.zig` and `make -C zigux phase8` now gate the current exec-cmd, help, kallsyms, libbpf cpu-mask, libbpf type-name, and segment-survey bundle together, so new Phase 8 tooling work should stay reviewable through that shared lane instead of widening into ad hoc per-slice checks.
- the current bounded Phase 8 decision is no longer whether `exec-cmd` still needs its pure `execl_cmd()` parity helper, whether `kallsyms.zig` still needs a direct parse wrapper, or whether `help.zig` still needs its pure pretty-print emission surface; those slices are now parked, so the next follow-up should come from the next helper-first libbpf segment or another still-active Phase 8 tooling slice.

Phase 9 notes
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
- `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `zigux/tests/phase9_build.zig` and `make -C zigux phase9` now gate the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together, so new Phase 9 runtime work should stay reviewable through that shared lane instead of widening into ad hoc per-slice checks.
- the current bounded Phase 9 decision is no longer whether the kretprobe lane still needs a starter, a survey gate, or shared build wiring; those pieces and the newer loader-handoff scaffold are now landed, so the next follow-up should be whichever small shared runtime loader substrate step can honestly consume the existing bitmap or kretprobe loader plans without widening into a larger runtime-module implementation.
