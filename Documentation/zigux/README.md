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

Phase 1 notes
- `Documentation/zigux/phase1-closure.md`
- `scripts/zigux/README.md`
- `zigux/Makefile`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/validate-phase1-closure.py`
- `scripts/zigux/check-phase1-parity.py`
- `scripts/zigux/check-phase1-bench.py`
- `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` keep the closed host-side helper packet reviewable through the shared helper build entrypoint and the Linux-style replay route, while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, and `zigux/Makefile` keep the closure and validator-first contract explicit from the docs root instead of leaving the Phase 1 packet split across later review surfaces.

Phase 2 notes
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `zigux/Makefile`
- `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py`, `make -C zigux phase2-validate`, and `make -C zigux phase2` now keep the pinned Zig toolchain, the bounded `fixdep`, `genksyms`, `genksyms_crc`, `kconfig`, and `mk_elfconfig` helper packet, the three-target compile matrix, and the shared tests-root plus review-checklist replay surface visible from the docs root instead of leaving the active Phase 2 tranche split across scripts, tests, and workflow wiring alone.

Phase 5 notes
- `Documentation/zigux/phase5-kfifo-sample-survey.md` now records the landed `samples/zigux/bytestream_fifo.zig` reference sample, its exact replay checks, and the remaining non-goals around procfs, user-copy, and module registration parity.
- the same Phase 5 survey note now doubles as the sample-backed contributor guide for the landed bytestream FIFO slice by naming the descriptor, manifest, and shared build-entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kobject-sample-survey.md` now records the landed `samples/zigux/kobject_example.zig` reference sample, its exact registration and attribute-roundtrip checks, and the remaining non-goals around sysfs creation, `kernel_kobj`, uevents, and module registration.
- the same kobject survey note now doubles as the sample-backed contributor guide for the landed kobject slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync.
- `Documentation/zigux/phase5-kretprobe-sample-survey.md` now records the landed `samples/zigux/kretprobe_example.zig` reference sample, its exact skip, private-data-shape, return-value, duration, and `nmissed` replay checks, and the remaining non-goals around probe registration, `pt_regs`, and module wiring.
- the same kretprobe survey note now doubles as the sample-backed contributor guide for the landed non-runtime `kretprobe` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime starter.
- `Documentation/zigux/phase5-trace-events-sample-survey.md` now records the landed `samples/zigux/trace_events_sample.zig` reference sample, its exact payload, string-selection, formatted-message, event-family-count, vararg-payload, relative-location, callback-path, and callback-registration replay checks, and the remaining non-goals around tracepoint macros, kernel scheduling, and module wiring.
- the same trace-events survey note now doubles as the sample-backed contributor guide for the landed non-runtime `trace-events` slice by naming the descriptor, manifest, and shared `phase5_build.zig` entrypoint prompts that reviewers should keep in sync while staying distinct from the separate Phase 9 runtime pilot tranche.
- the trace-events Phase 5 packet still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` reference sample, so reviewers should keep treating the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the formatting idiom cue while standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet.
- the Phase 5 notes now carry all four roadmap sample anchors as bounded `samples/zigux/` reference readings, while still keeping the separate Phase 9 runtime pilot tranche explicit for the same `trace-events` and `kretprobe` families.

Phase 4 notes
- `python3 scripts/zigux/validate-phase4.py` keeps the live `zigux/tests/atomic64_diff.zig` roadmap wrapper, its shared `zigux/tests/runtime_atomic64_diff.zig` backing replay, the manifest-backed `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` handoff survey, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` wired through the shared `zigux/tests/phase4_build.zig` entrypoint and the bootstrap workflow.
- `Documentation/zigux/phase4-validation-matrix.md` records the current Phase 4 rollback owners, threshold posture, and lab or CI replay matrix.

Phase 6 notes
- `Documentation/zigux/phase6-base64-slice.md`
- `Documentation/zigux/phase6-bsearch-slice.md`
- `Documentation/zigux/phase6-checksum-slice.md`
- `Documentation/zigux/phase6-hexdump-slice.md`
- `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/Makefile`, `make -C zigux phase6-validate`, and `make -C zigux phase6` now keep the current base64, bsearch, checksum, and hexdump helper bundle reviewable through the shared surface checker, the bundled replay, and the Linux-style helper lane together, so new helper slices should only land when that shared packet stays green as one unit.
- the current bounded Phase 6 decision is no longer whether one more tiny external fixture is still worth carrying; the live leaf-helper lane is the bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already kept reviewable through `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, and `make -C zigux phase6`, so future follow-up here should reopen only for a concrete parity gap or another similarly small helper-first step inside that same packet.

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
- `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, the four `samples/zigux/runtime_*_loader.zig` scaffolds, and `zigux/kernel/runtime_loader.zig` now keep the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle reviewable through one shared runtime-loader lane instead of widening into ad hoc per-slice checks or implying a dedicated shared `validate-phase9.py` surface that does not exist on `master`.
- the current bounded Phase 9 decision is no longer whether the runtime-pilot lane still needs starter samples, loader-handoff scaffolds, or a shared request surface; `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_trace_events_loader.zig`, and `zigux/kernel/runtime_loader.zig` are now in place, so the next follow-up should stay inside the smallest shared runtime-loader substrate or validation step that keeps those four handoffs reviewable without widening into a larger runtime-module implementation.

Phase 10 notes
- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `make -C zigux phase10` now keep the current virtio core, virtio ring, virtio input, and virtio mmio packet reviewable through the shared build-and-make lane, and there is still no dedicated shared `validate-phase10.py`, `check-phase10-harness-coverage.py`, or `phase10-validate` target on `master`.
- the current bounded Phase 10 decision is no longer whether the virtio core lane still needs config-change bookkeeping or reset-proof coverage; those pieces are now landed, so the next follow-up should stay in the smallest core-only or survey-backed virtio step that sharpens queue or device bookkeeping without widening into transport implementation churn.

Phase 11 notes
- `Documentation/zigux/phase11-bcm2835-wdt-slice.md`
- `Documentation/zigux/phase11-bcm2835-wdt-survey.md`
- `Documentation/zigux/phase11-gpio-wdt-slice.md`
- `Documentation/zigux/phase11-gpio-wdt-survey.md`
- `Documentation/zigux/phase11-dw-wdt-slice.md`
- `Documentation/zigux/phase11-dw-wdt-survey.md`
- `Documentation/zigux/phase11-hvc-console-slice.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `zigux/tests/phase11_build.zig` and `make -C zigux phase11` now gate the current bcm2835, gpio, and dw watchdog slices together with the hvc console tranche, so new Phase 11 work should stay reviewable through that shared lane instead of widening into ad hoc per-slice checks.
- `Documentation/zigux/phase11-shared-replay-contract.md` now records that same shared contributor packet, including `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, and `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and the dedicated `Documentation/zigux/phase11-hvc-console-survey.md` boundary beside the shared replay route.
- the current bounded Phase 11 decision is no longer whether the bcm2835 watchdog lane needs another ownership summary helper; those pieces are now landed, so the next follow-up should stay in one tiny hardware-validation matrix before any platform registration, PM base plumbing, or live poweroff-handler coordination is attempted.

Phase 12 notes
- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `zigux/tests/phase12_build.zig` and `make -C zigux phase12` now keep the current nvme pci, virtio_net, virtio_scsi, and libbpf survey-backed complex-driver bundle reviewable through the shipped Phase 12 build-and-make lane instead of implying removed validator or PMO checker surfaces.
- the current shared Phase 12 review surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `zigux/tests/phase12_build.zig`, the bounded Phase 12 nvme, virtio_net, virtio_scsi, and libbpf test modules wired through that build, the committed Phase 12 manifests under `zigux/tests/`, `tools/lib/bpf/zigux_segments/manifest.json`, and `zigux/Makefile`.
- there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`; future Phase 12 reviewability claims should name only shipped survey, build, and make surfaces until new validator files actually land.

Phase 13 notes
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-libfs-slice.md`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-slice.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `zigux/tests/phase13_build.zig`, `scripts/zigux/validate-phase13-release.py`, and `make -C zigux phase13` now keep the current libfs, devres, landlock ruleset, and landlock syscalls helper tranche reviewable through one shared Phase 13 release packet instead of leaving the active shared-subsystems lane visible only in packet-local surveys.
- the same top-level Phase 13 packet now also keeps the roadmap traceability note, the release survey, the four manifest-backed anchor packets, and the adjacent notifier-list reviewability packet visible from the docs root without changing the roadmap's four-anchor count.
- the current bounded Phase 13 decision is no longer whether the lane still needs its first shared-helper footholds; those starters and survey-backed replay surfaces are already present on `master`, so the next follow-up should stay inside one tiny release-surface, validator, or helper-truthfulness repair before any wider subsystem claims are reopened.

Phase 14 notes
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `zigux/tests/phase14_build.zig`
- `zigux/tests/phase14_end_to_end_smoke_survey.zig`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `make -C zigux phase14-smoke`
- `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`
- `make -C zigux phase14-test`
- `zig build test --build-file zigux/tests/phase14_build.zig --summary all`
- `make -C zigux phase14` now keep the current workqueue, ring-buffer, and skbuff-adjacent smoke packet reviewable through the shipped smoke-only and full replay routes instead of implying a removed validator stack or a direct deep-core port commitment.
- the current bounded Phase 14 decision is not whether `kernel/rcu/tree.c`, `net/core/skbuff.c`, or other freeze-map anchors are ready for a direct Zigux port; the active packet stays parked on shared smoke and release-boundary evidence, so the next follow-up should remain one tiny survey, manifest, docs-root, or tests-root truthfulness repair inside that study-only lane.

Phase 15 notes
- `Documentation/zigux/freeze-map.md`
- `Documentation/zigux/phase15-freeze-map-governance.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`
- `Documentation/zigux/phase15-parity-scorecard.md`
- `Documentation/zigux/phase15-indefinite-c-policy.md`
- `zigux/tests/phase15_build.zig` and `make -C zigux phase15` now keep the current freeze-map, dedicated freeze-map-governance note, Architecture Council review-process, parity-scorecard, dedicated indefinite-C policy note, and stay-in-C governance packet reviewable through one shared Phase 15 lane instead of widening into ad hoc deep-core status claims.
- the current bounded Phase 15 decision is not whether a freeze-in-C anchor is ready for a direct Zigux port; no Architecture Council approval is recorded yet, so the next follow-up should wait for a named reopen trigger or a real deep-core blocker-posture change before opening another governance slice.

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
- `scripts/zigux/validate_phase3_selftest.py` and `make -C zigux phase3-selftest` rerun the validator-local support packet through the shared runner when contributors want a focused check on the Phase 3 support scripts without duplicating the default `phase3-validate` route.
- `make -C zigux phase3-validate` runs the same lightweight Phase 3 validator, self-test, wrapper-check, and documentation-sync audit mix that the bootstrap workflow expects before the heavier parity steps.
- `python3 scripts/zigux/run-phase3-checks.py --list` shows the currently discovered Phase 3 parity slices.
- `python3 scripts/zigux/run-phase3-checks.py` executes the full discovered Phase 3 parity suite.

Windows note
- a Linux-scale checkout on NTFS must use a case-sensitive directory or a Linux filesystem
- otherwise case-colliding Linux paths will create false working-tree dirt on Windows
