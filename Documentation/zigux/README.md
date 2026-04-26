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

Phase 5 notes
- `Documentation/zigux/phase5-kfifo-sample-survey.md` now records the landed `samples/zigux/bytestream_fifo.zig` reference sample, its exact replay checks, and the remaining non-goals around procfs, user-copy, and module registration parity.
- the same Phase 5 survey note now doubles as the sample-backed contributor guide for the landed bytestream FIFO slice by naming the descriptor, manifest, and shared build-entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kobject-sample-survey.md` now records the landed `samples/zigux/kobject_example.zig` reference sample, its exact registration and attribute-roundtrip checks, and the remaining non-goals around sysfs creation, `kernel_kobj`, uevents, and module registration.
- the same kobject survey note now doubles as the sample-backed contributor guide for the landed kobject slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kretprobe-sample-survey.md` now records the landed `samples/zigux/kretprobe_example.zig` reference sample, its exact skip, private-data-shape, return-value, duration, and `nmissed` replay checks, and the remaining non-goals around probe registration, `pt_regs`, and module wiring.
- the same kretprobe survey note now doubles as the sample-backed contributor guide for the landed non-runtime `kretprobe` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime starter.
- `Documentation/zigux/phase5-trace-events-sample-survey.md` now records the landed `samples/zigux/trace_events_sample.zig` reference sample, its exact payload, string-selection, formatted-message, event-family-count, vararg-payload, relative-location, callback-path, and callback-registration replay checks, and the remaining non-goals around tracepoint macros, kernel scheduling, and module wiring.
- the same trace-events survey note now doubles as the sample-backed contributor guide for the landed non-runtime `trace-events` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime starter.
- the Phase 5 notes now carry all four roadmap sample anchors as bounded `samples/zigux/` reference readings, while still keeping the separate Phase 9 runtime pilot tranche explicit for the same `trace-events` and `kretprobe` families.

Phase 4 notes
- `python3 scripts/zigux/validate-phase4.py` keeps the live `zigux/tests/runtime_atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` rollback gates wired through the shared `zigux/tests/phase4_build.zig` entrypoint and the bootstrap workflow.
- `Documentation/zigux/phase4-validation-matrix.md` records the current Phase 4 rollback owners, threshold posture, and lab or CI replay matrix.

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
- the current bounded Phase 8 decision is no longer whether `exec-cmd` still needs its pure `execl_cmd()` parity helper; that slice is now parked, so the next follow-up should come from sibling files such as `help.zig`, `kallsyms.zig`, or the next helper-first libbpf segment.

Phase 3 notes
- Active Phase 3 slices are discovered from `phase3-*-slice.md` records instead of being duplicated in multiple hand-maintained inventories.
- `python3 scripts/zigux/validate-phase3.py` validates every discovered slice and its preferred manifest, accepts either the shared runner gate (`python3 scripts/zigux/run-phase3-checks.py --slug <slug>`) or a legacy per-slice wrapper gate in each slice record, reports obsolete `check-phase3-*.py` wrapper files that no longer belong to a discovered slice, and rejects legacy wrapper script paths inside Phase 3 manifests so those manifests remain a record of slice artifacts rather than compatibility entrypoints.
- `python3 scripts/zigux/phase3_catalog.py --self-test`, `python3 scripts/zigux/phase3_check_lib.py --self-test`, and `python3 scripts/zigux/run-phase3-checks.py --self-test` cover the discovery, shared-helper, and slug-selection paths without launching the full parity suite.
- `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-docs` lists the discovered slice records that still reference legacy per-slice wrapper commands, which makes wrapper-reference cleanup auditable instead of manual.
- `python3 scripts/zigux/phase3_catalog.py --rewrite-shared-runner-docs` rewrites those legacy record references to the shared runner command in place, which makes incremental cleanup repeatable.
- `python3 scripts/zigux/phase3_catalog.py --legacy-wrapper-references` lists remaining discovered Phase 3 wrapper mentions in non-slice documentation, so policy-doc cleanup stays auditable after the manifest references were removed.
- `python3 scripts/zigux/phase3_catalog.py --rewrite-legacy-wrapper-references` rewrites those non-slice documentation references to the shared runner command in place, which gives `artifact-diff.md` and related policy docs the same scripted cleanup path as the slice records.
- `python3 scripts/zigux/phase3_catalog.py --rewrite-artifact-diff-phase3-section` regenerates the detailed `Documentation/zigux/artifact-diff.md` Phase 3 policy block from the current discovered slice catalog.
- `python3 scripts/zigux/phase3_catalog.py --audit-doc-sync` reports stale non-slice wrapper references plus a stale artifact-diff Phase 3 block, and bootstrap now runs it so documentation drift fails fast.
- `python3 scripts/zigux/phase3_catalog.py --suggest-slug-renames` now keeps the slug cleanup report conservative by requiring a suspicious long slug and its shorter prefix to agree on normalized fixture-manifest structure and `expected.json` schema before it suggests a rename.
- `python3 scripts/zigux/generate-phase3-check-wrappers.py --check` catches wrapper-template drift and obsolete wrapper files before the parity suite runs.
- `make -C zigux phase3-validate` runs the same lightweight Phase 3 validator, self-test, wrapper-check, and documentation-sync audit mix that the bootstrap workflow expects before the heavier parity steps.
- `python3 scripts/zigux/run-phase3-checks.py --list` shows the currently discovered Phase 3 parity slices.
- `python3 scripts/zigux/run-phase3-checks.py` executes the full discovered Phase 3 parity suite.

Windows note
- a Linux-scale checkout on NTFS must use a case-sensitive directory or a Linux filesystem
- otherwise case-colliding Linux paths will create false working-tree dirt on Windows
