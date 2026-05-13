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

Phase 3 notes
- `Documentation/zigux/phase3-roadmap-gap-survey.md` now maps the original Phase 3 roadmap anchors `rust/exports.c`, `lib/bitmap.c`, `lib/rbtree.c`, and `lib/cpumask.c` to the live ABI substrate, the current export shim and current `zigux/uapi/version.zig` boundary, and the current interop slices, so reviewers can see in one place which anchors are already covered, which adjacent helpers are real repo state, and which roadmap-backed gap is still open.
- `scripts/zigux/validate-phase3-roadmap-gap-survey.py`, `make -C zigux phase3-validate`, and the bootstrap workflow now keep that survey note explicit, including the narrow export shim and current `zigux/uapi/version.zig` boundary, the current `rbtree` gap, and the note that the longer `chrdev_*` planning ladder should not be mistaken for roadmap closure.
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md` now records the narrower export-shim and UAPI boundary reality inside the same Phase 3 substrate: `zigux/kernel/export_shim.zig` remains a narrow explicit-status helper with a shared boundary-header path, `zigux/uapi/` remains bounded to `zigux/uapi/version.zig`, and the broader curated UAPI surface is still intentionally deferred.
- `scripts/zigux/validate-phase3-export-uapi-survey.py` and `make -C zigux phase3-validate` now keep that dedicated export-shim and UAPI boundary survey packet explicit alongside the broader roadmap-gap note.
- `Documentation/zigux/phase3-abi-slice.md` now also records the published focused policy-and-unsafe substrate gate around `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, and `zigux/unsafe/narrow.zig`, including the explicit `raw_pointer_bridge` unsafe scope plus the dedicated `zigux/tests/phase3_policy_unsafe.zig` replay path.
- `scripts/zigux/validate-phase3.py`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and `make -C zigux phase3-validate` now keep that focused Phase 3 policy-and-unsafe packet explicit instead of leaving the helper family implied only by the broader ABI substrate bundle.

Phase 5 notes
- `Documentation/zigux/phase5-kfifo-sample-survey.md` now records the landed `samples/zigux/bytestream_fifo.zig` reference sample, its exact replay, non-destructive snapshot, preview-truncation, fixed embedded backing, and lifecycle-boundary checks, and the remaining non-goals around procfs, user-copy, locking, and module registration parity.
- the same Phase 5 survey note now doubles as the sample-backed contributor guide for the landed bytestream FIFO slice by naming the descriptor, manifest, and shared build-entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kobject-sample-survey.md` now records the landed `samples/zigux/kobject_example.zig` reference sample, its exact registration, Linux `foo`/`baz`/`bar` attribute-order, and attribute-roundtrip checks, and the remaining non-goals around sysfs creation, `kernel_kobj`, uevents, and module registration.
- the same kobject survey note now doubles as the sample-backed contributor guide for the landed kobject slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kretprobe-sample-survey.md` now records the landed `samples/zigux/kretprobe_example.zig` reference sample, its exact skip, private-data-shape, return-value, duration, fixed `maxactive`, and `nmissed` replay checks, and the remaining non-goals around probe registration, `pt_regs`, and module wiring.
- the same kretprobe survey note now doubles as the sample-backed contributor guide for the landed non-runtime `kretprobe` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime starter.
- `Documentation/zigux/phase5-trace-events-sample-survey.md` now records the landed `samples/zigux/trace_events_sample.zig` reference sample, its exact payload, string-selection, main-path and callback-path iteration cues, formatted-message, event-family-count, vararg-payload, relative-location, callback-path, and callback-registration replay checks, and the remaining non-goals around tracepoint macros, kernel scheduling, and module wiring.
- the same trace-events survey note now doubles as the sample-backed contributor guide for the landed non-runtime `trace-events` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime pilot tranche.
- the Phase 5 notes now carry all four roadmap sample anchors as bounded `samples/zigux/` reference readings, while still keeping the separate Phase 9 runtime pilot tranche explicit for the same `trace-events` and `kretprobe` families.

Phase 4 notes
- `make -C zigux phase4-validate` runs `python3 scripts/zigux/artifact_diff.py --self-test` plus `python3 scripts/zigux/validate-phase4.py` before the shared Phase 4 Zig diff gates.
- `python3 scripts/zigux/check-artifact-diff-contract.py` now gives the same Phase 4 validation path one external replay of the actual `artifact_diff.py` CLI contract, covering one stable pass case plus one missing-file failure shape so the outward `ARTIFACT_DIFF=...` lines do not live only inside the helper's built-in self-test.
- `python3 scripts/zigux/validate-phase4.py` keeps the live `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_survey.zig`, and `zigux/tests/bitmap_diff.zig` rollback gates plus survey evidence, the shared `zigux/tests/phase4_build.zig` entrypoint, the bootstrap workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`, and the directly coupled Phase 4 notes aligned.
- `Documentation/zigux/phase4-validation-matrix.md` records the current Phase 4 rollback owners, threshold posture, the shared `phase4-runtime-atomic64-diff-tests`, `phase4-runtime-atomic64-diff-survey-tests`, and `phase4-bitmap-diff-tests` build entries plus the dedicated `phase4-runtime-atomic64-diff` and `phase4-bitmap-diff` local replay steps that keep each shipped gate measurable, and the reversible-delivery evidence that ties each shipped gate back to its current C anchor if the shared Phase 4 entrypoint has to drop that Zig gate.

Phase 6 notes
- `Documentation/zigux/phase6-base64-slice.md`
- `Documentation/zigux/phase6-bsearch-slice.md`
- `Documentation/zigux/phase6-checksum-slice.md`
- `Documentation/zigux/phase6-hexdump-slice.md`
- `python3 scripts/zigux/validate-phase6.py` and `make -C zigux phase6-validate` now fail fast if the shared Phase 6 leaf-helper bundle drifts out of sync across `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the bootstrap workflow, and the published slice notes.
- `zigux/tests/phase6_build.zig` and `make -C zigux phase6` now gate the current base64, bsearch, checksum, and hexdump helper bundle together, so new helper slices should only land when that shared lane stays green as one unit.
- `make -C zigux phase6-checksum-perf` now replays a checksum-specific perf sanity harness so the current math-sensitive helper lane records representative per-call and per-byte cost before Phase 6 claims it is ready to park.
- `make -C zigux phase6-hexdump-perf` now replays a hexdump-specific perf sanity harness so the current formatter-sensitive helper lane records representative dump cost for plain and ASCII paths before Phase 6 treats that slice as fully parked.
- the current bounded Phase 6 decision is no longer whether the hexdump fixture wiring works in CI; it is whether the current bsearch, checksum, and hexdump parity evidence is sufficient to park the leaf-helper lane or whether one more tiny external fixture is still worth carrying.

Phase 7 notes
- `Documentation/zigux/phase7-string-helpers-slice.md`
- `Documentation/zigux/phase7-cmdline-slice.md`
- `Documentation/zigux/phase7-argv-split-slice.md`
- `Documentation/zigux/phase7-rbtree-slice.md`
- `zigux/tests/phase7_build.zig` and `make -C zigux phase7` now gate the current string-helpers, cmdline, argv-split, and rbtree helper bundle together, so Phase 7 helper work should stay reviewable through that shared lane instead of adding ad hoc per-slice CI steps.
- the Phase 7 string-helpers bundle now also carries `samples/zigux/string_helpers_sample.zig`, the manifest-backed `zigux/tests/phase7_string_helpers_sample_manifest.json` and `zigux/tests/phase7_string_helpers_sample_survey.zig` packet, and the explicit sample-root boundary guard in `samples/zigux/README.md` plus `zigux/tests/phase7_string_helpers_sample_boundary.zig`, so the bounded sample replay, the exact-fit unescape and bounded escape-window proofs, and the no-fifth-anchor note stay tied to the helper lane instead of reading like a new Phase 5 anchor.
- the Phase 7 helper bundle is now parked end-to-end: cmdline, argv-split, rbtree, and the bounded string-helpers slice all carry their current dedicated proofs through the shared `phase7_build.zig` gate, so future work here should reopen only for a concrete newly observed parity gap rather than for more speculative fixture expansion.

Phase 8 notes
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-help-slice.md`
- `Documentation/zigux/phase8-kallsyms-slice.md`
- `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`
- `Documentation/zigux/phase8-bpf-type-names-slice.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `python3 scripts/zigux/validate-phase8.py` and `make -C zigux phase8-validate` now fail fast if the shared Phase 8 tooling bundle drifts out of sync across `zigux/tests/phase8_build.zig`, `zigux/Makefile`, the bootstrap workflow, the shared README notes, and the current libbpf helper-family survey around `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, and `tools/lib/bpf/zigux_segments/type_names.zig`.
- `zigux/tests/phase8_build.zig` and `make -C zigux phase8` now gate the current exec-cmd, help, kallsyms, libbpf cpu-mask, libbpf logging, libbpf pin-path, libbpf type-name, and segment-survey bundle together, so new Phase 8 tooling work should stay reviewable through that shared lane instead of widening into ad hoc per-slice checks.
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
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` and `Documentation/zigux/review-checklist.md` now carry the shared loader-handoff release-discipline evidence for the current runtime bundle, so the bounded Phase 9 lane stays explicit about allocator ownership, `requires_runtime_substrate`, handoff stage, and the still-blocked command or environment control surface.
- the same Phase 9 loader-gap bundle now keeps a manifest-backed catalog and ownership map in `zigux/tests/runtime_loader_gap_manifest.json`, so reviewers can see which file owns the survey note, checklist, shared request contract, sample-side loader plans, and shared `phase9_build.zig` replay path before the lane widens again.
- the `Documentation/zigux/phase9-runtime-trace-events-{survey,module-slice}.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` bundle now keeps the `Documentation/zigux/freeze-map.md` boundary explicit, so `kernel/trace/ring_buffer.c` stays `Study / Boundary Only` and any trace-core status change still requires an Architecture Council decision.
- `python3 scripts/zigux/validate-phase9.py` and `make -C zigux phase9-validate` now fail fast if the shared Phase 9 checklist, loader-gap survey, trace-events freeze-map boundary packet, README notes, workflow wiring, and `zigux/tests/phase9_build.zig` entrypoint drift apart.
- `zigux/tests/phase9_build.zig` and `make -C zigux phase9` now gate the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together, so new Phase 9 runtime work should stay reviewable through that shared lane instead of widening into ad hoc per-slice checks.
- the current bounded Phase 9 decision is no longer whether the kretprobe lane still needs a starter, a survey gate, or shared build wiring; those pieces and the newer loader-handoff scaffold are now landed, so the next follow-up should be whichever small shared runtime loader substrate step can honestly consume the existing bitmap or kretprobe loader plans without widening into a larger runtime-module implementation.

Phase 10 notes
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `Documentation/zigux/phase10-closure-evidence.md` now records the exact current roadmap-aligned virtio lab bundle and keeps Phase 10 explicit as active rather than prematurely closed while `drivers/virtio/virtio_mmio.zig` remains intentionally absent.
- `python3 scripts/zigux/validate-phase10-closure.py` and `make -C zigux phase10-validate` now fail fast if the shared closure note, the three manifest-backed survey records, the bootstrap workflow, and `zigux/tests/phase10_build.zig` drift apart.
- `zigux/tests/phase10_build.zig` and `make -C zigux phase10` now gate the current virtio core, ring, input, and MMIO-survey evidence bundle together, so new Phase 10 work stays reviewable as one bounded lab tranche instead of widening into ad hoc transport claims.

Phase 13 notes
- `Documentation/zigux/phase13-roadmap-traceability.md` now maps the four roadmap anchors from Phase 13's shared subsystem-helper tranche to the current repo evidence so reviewers can trace `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c` from roadmap to code, tests, manifests, and survey notes without hunting through the tree.
- `Documentation/zigux/phase13-release-notes-survey.md` now records the current release-discipline reading for the active shared-helper tranche, keeps the current roadmap-aligned evidence bundle in one place, and states plainly that Phase 13 is still active rather than closed while `lib/devres.c` remains the only anchor without a manifest-backed survey packet.
- `zigux/tests/phase13_build.zig` and `make -C zigux phase13` are the shared tranche entrypoints for the current `libfs`, `devres`, `landlock/ruleset`, and `landlock/syscalls` helper packet, so Phase 13 follow-up should stay reviewable through that bundle instead of widening into ad hoc checks.
- `Documentation/zigux/phase13-libfs-slice.md`, `Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, and `Documentation/zigux/phase13-notifier-list-survey.md` are the current published Phase 13 slice surfaces.
- `zigux/tests/phase13_notifier_list_reviewability.zig` and `zigux/tests/phase13_notifier_list_manifest.json` now keep one adjacent Phase 13 reviewability packet explicit around the preexisting list or hlist helper surface, the chrdev-local notifier planner, and the still-missing generic notifier ABI or helper gap without presenting that survey as a fifth roadmap anchor.
- the current bounded Phase 13 documentation gap is no longer whether the top-level docs expose the shared-helper tranche at all; that pointer now exists here, while `lib/devres.c` remains the only active Phase 13 roadmap anchor without the same manifest-backed survey packet already carried by `libfs` and the two Landlock anchors.

Phase 14 notes
- `Documentation/zigux/phase14-core-boundary-traceability.md` now maps the roadmap posture for the Phase 14 ring-buffer, skbuff, and RCU anchors to the current manifest-backed evidence on `master`, so reviewers can see in one place which anchor remains study-only, which anchors remain freeze-in-C, which surveyed commits are current, and which stay-in-C concurrency decisions are still owned by the shipped C implementation.
- the new Phase 14 note is intentionally cross-anchor and notes-only: it points at `zigux/tests/phase14_ring_buffer_manifest.json`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, `zigux/tests/phase14_rcu_tree_manifest.json`, and `Documentation/zigux/phase14-end-to-end-smoke-survey.md` without reopening anchor-local implementation work or overlapping the existing ring-buffer, skbuff, RCU, or shared-smoke lanes.
- `zigux/tests/phase14_build.zig`, `make -C zigux phase14-validate`, and `make -C zigux phase14` remain the shared replay path for the current Phase 14 evidence bundle, so follow-up in this tranche should keep the roadmap posture, the anchor-local manifests, and the shared smoke packet aligned rather than inventing fresh bridge momentum.

Phase 15 notes
- `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, and `Documentation/zigux/phase15-indefinite-c-policy.md` now form the current long-term governance bundle for the freeze-in-C anchors, so reviewers can open the freeze boundary, the freeze-map maintenance note, the review-process rules, the parity scorecard, and the indefinite-C policy from the top-level docs index instead of hunting across unrelated phase notes.
- `Documentation/zigux/phase15-evidence-archives/` now carries the reserved per-anchor decision-record templates that the scorecard and review-process note point at for `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`.
- `Documentation/zigux/phase15-handoff-next-steps-survey.md` now keeps the parked-next-step synthesis in one place, so later runs can open the roadmap contract, ledger anchor, shared replay coverage, current handoff surface, open blocker posture, and maintenance-mode next step without hunting across the wider governance packet.
- `zigux/tests/phase15_build.zig` and `make -C zigux phase15` remain the shared replay path for the current Phase 15 governance bundle, so follow-up here should stay in maintenance mode until one of the named reopen triggers fires or the deep-core blocker posture changes.
