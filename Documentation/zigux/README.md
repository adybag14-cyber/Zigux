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
- `scripts/zigux/validate-phase3-roadmap-gap-survey.py`, `make -C zigux phase3-validate`, and the bootstrap workflow now keep that survey note explicit, including the narrow export shim and current `zigux/uapi/version.zig` boundary, the current `rbtree` gap, the existing Phase 1 and Phase 7 `rbtree` evidence that does not yet close the Phase 3 boundary packet, and the note that the longer `chrdev_*` planning ladder should not be mistaken for roadmap closure.
- `Documentation/zigux/phase3-export-uapi-boundary-survey.md` now records the narrower export-shim and UAPI boundary reality inside the same Phase 3 substrate: `zigux/kernel/export_shim.zig` remains a narrow explicit-status helper with a shared boundary-header path, `zigux/uapi/` remains bounded to `zigux/uapi/version.zig`, and the broader curated UAPI surface is still intentionally deferred.
- `scripts/zigux/validate-phase3-export-uapi-survey.py` and `make -C zigux phase3-validate` now keep that dedicated export-shim and UAPI boundary survey packet explicit alongside the broader roadmap-gap note.
- `Documentation/zigux/phase3-abi-slice.md` now also records the published focused policy-and-unsafe substrate gate around `zigux/helpers/layout_assert.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/unsafe/narrow.zig`, and the directly coupled scoped MMIO wrappers in `zigux/helpers/mmio.zig`, including explicit `raw_pointer_bridge` and `volatile_mmio` scope enforcement, allocator-owned init and reset requirements, overflow-checked unsafe address math, and the dedicated `zigux/tests/phase3_policy_unsafe.zig` replay path.
- `scripts/zigux/validate-phase3.py`, `zigux/tests/fixtures/phase3_abi_manifest.json`, and `make -C zigux phase3-validate` now keep that focused Phase 3 policy-and-unsafe packet explicit, including the interop-policy unsafe-byte decoding contract, allocator init and reset requirements, scoped narrow-unsafe plus MMIO helper path, and the validator self-test coverage for the layout, panic, allocator, and narrow-unsafe source markers, instead of leaving the family implied only by the broader ABI substrate bundle.

Phase 5 notes
- `samples/zigux/README.md` is the shared Phase 5 sample-root catalog for the four bounded reference samples and the later `runtime_*` starters that live in the same directory, so reviewers can keep the approved idiom lane distinct from Phase 9 runtime follow-ons.
- the same sample-root catalog now also carries the explicit string-work boundary checks that keep those four Phase 5 anchors distinct from the separate Phase 7 helper bundle rooted in `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, and `zigux/tests/phase7_build.zig`.
- the same sample-root catalog also keeps the current no-`samples/zigux/*cmdline*` boundary explicit, so cmdline evidence stays under the separate Phase 7 helper bundle rooted in `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_build.zig` instead of looking like a missing Phase 5 sample port.
- `Documentation/zigux/phase5-kfifo-sample-survey.md` now records the landed `samples/zigux/bytestream_fifo.zig` reference sample, its exact replay, non-destructive snapshot, preview-truncation, fixed embedded backing, and lifecycle-boundary checks, and the remaining non-goals around procfs, user-copy, locking, and module registration parity.
- the same Phase 5 survey note now doubles as the sample-backed contributor guide for the landed bytestream FIFO slice by naming the descriptor, `samples/zigux/README.md` catalog boundary, manifest, and shared build-entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kobject-sample-survey.md` now records the landed `samples/zigux/kobject_example.zig` reference sample, its exact registration, Linux `foo`/`baz`/`bar` attribute-order, and attribute-roundtrip checks, and the remaining non-goals around sysfs creation, `kernel_kobj`, uevents, and module registration.
- the same kobject survey note now doubles as the sample-backed contributor guide for the landed kobject slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kretprobe-sample-survey.md` now records the landed `samples/zigux/kretprobe_example.zig` reference sample, its exact skip, private-data-shape, return-value, duration, fixed `maxactive`, and `nmissed` replay checks, and the remaining non-goals around probe registration, `pt_regs`, and module wiring.
- the same kretprobe survey note now doubles as the sample-backed contributor guide for the landed non-runtime `kretprobe` slice by naming the descriptor, shared sample-root catalog, shared review checklist, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime starter.
- `Documentation/zigux/phase5-trace-events-sample-survey.md` now records the landed `samples/zigux/trace_events_sample.zig` reference sample, its exact payload, string-selection, main-path and callback-path iteration cues, formatted-message, event-family-count, vararg-payload, relative-location, callback-path, and callback-registration replay checks, and the remaining non-goals around tracepoint macros, kernel scheduling, and module wiring.
- the same trace-events survey note now doubles as the sample-backed contributor guide for the landed non-runtime `trace-events` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime pilot tranche.
- the Phase 5 notes now carry all four roadmap sample anchors as bounded `samples/zigux/` reference readings, while still keeping the separate Phase 9 runtime pilot tranche explicit for the same `trace-events` and `kretprobe` families.
- `python3 scripts/zigux/validate-phase5.py` and `make -C zigux phase5-validate` now fail fast if the shared Phase 5 sample packet drifts out of sync across `samples/zigux/README.md`, the four sample-backed survey notes, the four manifests, `zigux/tests/phase5_build.zig`, `zigux/Makefile`, and the bootstrap workflow.
- `zigux/tests/phase5_build.zig` and `make -C zigux phase5` now gate the current bytestream FIFO, kobject, kretprobe, and trace-events reference samples together through that same validator-first lane, so future Phase 5 work stays reviewable as one bounded contributor packet instead of ad hoc per-sample CI claims.

Phase 8 notes
- `Documentation/zigux/phase8-exec-cmd-slice.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`, `Documentation/zigux/phase8-bpf-type-names-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, and `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` are the current shared Phase 8 notes for repo-hosted tooling.
- the active Phase 8 packet keeps `tools/lib/subcmd/exec-cmd.zig`, `tools/lib/subcmd/help.zig`, `tools/lib/symbol/kallsyms.zig`, and the helper-first `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, `tools/lib/bpf/zigux_segments/pin_path.zig`, and `tools/lib/bpf/zigux_segments/type_names.zig` explicit as bounded tooling-side parity work rather than new process-launch, procfs, bpffs, or object-lifecycle claims.
- `python3 scripts/zigux/validate-phase8.py`, `make -C zigux phase8-validate`, `make -C zigux phase8`, `zigux/tests/phase8_help_only_build.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig` now keep the current Phase 8 flow reviewable across the focused subcmd, symbol, and segmented libbpf shards plus the shared tooling bundle.

Phase 10 notes
- `Documentation/zigux/README.md` now exposes the shared Phase 10 closure note plus the same nine published Phase 10 docs named by the shared closure packet, including `Documentation/zigux/phase10-virtio-core-survey.md` and `Documentation/zigux/phase10-virtio-mmio-slice.md`, so the top-level docs index does not undercount the live parity-evidence bundle.
- `Documentation/zigux/phase10-closure-evidence.md` now records the exact current roadmap-aligned virtio lab bundle and keeps Phase 10 explicit as active rather than prematurely closed while `drivers/virtio/virtio_mmio.zig`, its bounded MMIO starter test, and the remaining risky transport gaps stay visible together.
- `python3 scripts/zigux/validate-phase10-closure.py` and `make -C zigux phase10-validate` now fail fast if the shared closure note, the four Phase 10 survey manifests, the bootstrap workflow, and `zigux/tests/phase10_build.zig` drift apart.
- `python3 scripts/zigux/validate-phase10.py` and `make -C zigux phase10-validate` now keep the wider Phase 10 input-plus-MMIO starter packet explicit across `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, the landed registration-preflight helper, the landed queue-callback preflight helper, and the remaining registration-lifecycle blocker so the shared docs index still matches the shipped validation surface.

Phase 11 notes
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-uapi-header-parity-survey.md` are the current shared delivery packet for the active simple-driver tranche.
- the active Phase 11 simple-driver packet now keeps the four roadmap-backed driver lanes visible from the top-level docs index while keeping the paired UAPI header parity survey explicit as the shared tranche-close boundary.
- `python3 scripts/zigux/validate-phase11.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `make -C zigux phase11-validate`, and `make -C zigux phase11` now define the shared Phase 11 reviewability path, with the dedicated `zigux/tests/phase11_hvc_console_survey.zig` archival replay still kept separate from `zigux/tests/phase11_build.zig`.
