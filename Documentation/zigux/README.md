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
- `Documentation/zigux/phase2-closure.md`
Phase 1 notes
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase1-closure.py`
- `scripts/zigux/check-phase1-string-review-packet.py`
- `scripts/zigux/check-phase1-direct-owner-markers.py`
- `scripts/zigux/check-phase1-bench.py`
keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again even though its live body still exposes only the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes.
  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.
  * keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.
  * `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.
Phase 2 notes
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `python3 scripts/zigux/check-zig-toolchain.py --self-test`
- `python3 scripts/zigux/check-zig-toolchain.py --policy-only`
- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/zig-toolchain-policy.json`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
now keep the current directly readable Phase 2 toolchain, closure-side, kbuild, kconfig bridge, make-wrapper, and artifact-support packet visible from the docs root instead of rebuilding the older installer and direct cross-route stack from missing current-`master` paths.
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`, so treat those installer and direct cross-route names as historical packet members until same-lane work rematerializes them on `master`.
  * keep the docs-root Phase 2 summary aligned to the shipped toolchain checker, the docs-shared-reminder checker, the required-make-route guard, the pinned Zig toolchain policy, the surviving kbuild and alignment guards, the live `conf_bridge` plus `confdata_bridge` helpers, `zigux/Makefile`, the current artifact-support manifest, the current kconfig fixture roster, and the current reminder routes `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.
  * keep the pinned policy-only and archive-integrity replays explicit without reviving missing installer or direct cross-route proof text.
Phase 3 notes
- `Documentation/zigux/phase3-abi-slice.md`
- `Documentation/zigux/phase3-errptr-xarray-slice.md`
- `Documentation/zigux/phase3-policy-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `Documentation/zigux/phase3-shared-reminder-gap.md`
- `include/linux/zigux.h`
- `include/zigux/dev_t.h`
- `include/zigux/abi.h`
- `zigux/uapi/version.zig`
- `zigux/uapi/dev_t.zig`
- `zigux/bindings/abi.zig`
- `zigux/bindings/dev_t.zig`
- `zigux/bindings/version.zig`
- `zigux/kernel/export_shim.zig`
- `zigux/helpers/err_ptr.zig`
- `zigux/helpers/xa_value.zig`
- `zigux/helpers/panic_policy.zig`
- `zigux/helpers/allocator_policy.zig`
- `zigux/helpers/unsafe_policy.zig`
- `zigux/tests/phase3_dev_t_starter_packet.zig`
- `zigux/tests/phase3_dev_t_starter_packet_build.zig`
- `zigux/tests/phase3_dev_t_starter_packet_manifest.json`
- `zigux/tests/phase3_errptr_xarray_starter_packet.zig`
- `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet.zig`
- `zigux/tests/phase3_policy_starter_packet_build.zig`
- `zigux/tests/phase3_policy_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
now keep the current Phase 3 reminder surface anchored to one bounded `dev_t` starter packet with its directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` slice, one focused helper-local policy slice, and the now-shipped export/UAPI boundary reminder packet, instead of presenting broader catalog, low-level-wrapper, or shared replay surfaces as the whole docs-root Phase 3 story on current `master`.
  * the docs-root Phase 3 summary should keep the current starter packet explicit through `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/version.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_dev_t_starter_packet_manifest.json`, and the dedicated `scripts/zigux/check-phase3-dev-t-starter-packet.py` checker, while the helper-local interop slice stays explicit through `Documentation/zigux/phase3-errptr-xarray-slice.md`, `zigux/helpers/err_ptr.zig`, `zigux/helpers/xa_value.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, and `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`, and the focused policy slice stays explicit through `Documentation/zigux/phase3-policy-slice.md`, `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, and `scripts/zigux/check-phase3-policy-starter-packet.py`.
  * keep the docs-root Phase 3 export boundary wording limited to what the current direct-readback path actually proves: `Documentation/zigux/phase3-kernel-export-shim-governance.md`, `zigux/bindings/notifier_abi.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, and the direct `make -C zigux phase3-export-uapi-layout-test` convenience route keep the returned kernel-facing export note, notifier-binding companion, and focused layout replay explicit from the docs root, while `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `Documentation/zigux/phase3-linux-zigux-header-governance.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `zigux/tests/fixtures/phase3_abi_manifest.json` should stay framed as repo-reality gaps until authenticated direct readback returns them again; `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/helpers/atomic.zig`, `zigux/helpers/barrier.zig`, `zigux/helpers/mmio.zig`, `zigux/unsafe/narrow.zig`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig` keep the current bounded atomic, barrier, and MMIO wrapper reminder packet explicit; keep `Documentation/zigux/phase3-shared-reminder-gap.md` explicit as the tracker for the remaining tests-root reminder follow-through rather than reopening broader saved Phase 3 publication packets.
Phase 4 notes
- `Documentation/zigux/phase4-reversible-delivery-evidence.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase4-repo-reality-warning.py`
- `scripts/zigux/check-phase4-reversible-delivery-pins.py`
Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` now keep the current direct-readback rollback packet reviewable from the docs root while the recovered gate-evidence and validation-matrix note pair, the dedicated local-only perf packet, and the roadmap-backed atomic64 differential-gate pair stay explicit as current direct-readback companions, and only the broader checker, validator, build, and bitmap-diff companions remain repo-reality gaps on current `master`.
  * keep the current direct-readback companion split explicit from the docs root too: `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `zigux/tests/atomic64_diff.zig`, and `zigux/tests/runtime_atomic64_diff.zig` are directly readable current-head evidence, while `scripts/zigux/check-phase4-gate-evidence.py`, `scripts/zigux/check-phase4-remaining-gap-matrix.py`, `scripts/zigux/validate-phase4.py`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` should stay framed as broader repo-reality gaps until fresh authenticated readback restores them.
  * keep the pending shared-CI perf-promotion posture explicit instead of implying the directly readable local-only perf packet or the still-missing broader Phase 4 checker-and-build routes are already shared-CI-approved current-head evidence.
Phase 5 notes
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
now keep the current shared Phase 5 reminder packet explicit from the docs root so contributor guidance still matches the four approved non-runtime sample anchors without inventing new sample behavior or runtime proof.
  * the docs-root Phase 5 summary should stay aligned with `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, and `zigux/tests/README.md`, and it should keep the same four roadmap-backed anchors explicit: `samples/kfifo/bytestream-example.c`, `samples/kobject/kobject-example.c`, `samples/kprobes/kretprobe_example.c`, and `samples/trace_events/trace-events-sample.c`.
  * keep the current shared packet truthful here too: `Documentation/zigux/phase5-kfifo-sample-survey.md` plus `samples/zigux/bytestream_fifo.zig` keep the restored direct bytestream note-and-sample proof explicit, `samples/zigux/kretprobe_example.zig` is the directly readable non-runtime sample-root proof for the restored kretprobe packet, and `samples/zigux/trace_events_string_formatting_sample.zig` remains the bounded direct trace-events formatting companion rather than a returned full trace-events port or a fifth sample; keep `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` framed as current public-tree-backed trace-events companion evidence, while `samples/zigux/kobject_example.zig` and the shared `zigux/tests/phase5_build.zig` route stay in split-readback companion or repo-reality-gap wording until a fresh reread proves broader direct authenticated proof again.
  * keep the no-extra-sample boundaries explicit from this docs root too: there is no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` reference sample on current `master`, and the bounded `*string*` companion stays tied to the non-runtime trace-events anchor rather than helper-local delivery.
  * keep the Phase 5 versus Phase 9 boundary explicit: do not count `samples/zigux/runtime_*.zig` files as extra Phase 5 evidence, and do not widen this docs-root reminder into runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer claims while the freeze map keeps those later lanes separate.
Phase 6 notes
- `Documentation/zigux/phase6-helper-evidence-catalog.md`
- `zigux/tests/phase6_helper_evidence_manifest.json`
- `scripts/zigux/check-phase6-shared-surface.py`
- `scripts/zigux/check-phase6-present-entrypoints.py`
now keep the current Phase 6 docs-root reminder packet explicit from the documentation root so current helper parity and perf follow-through stays bounded to the directly readable shared evidence packet without widening into new helper semantics.
  * repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`, so treat those broader parity and perf reminder paths as historical packet members that need fresh reread or re-materialization before they are reused here as direct current-`master` docs-root evidence.
  * keep the docs-root Phase 6 summary aligned with `Documentation/zigux/phase6-helper-evidence-catalog.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, and `scripts/zigux/check-phase6-present-entrypoints.py`, so the shared helper packet keeps the bounded base64, bsearch, checksum, and hexdump evidence rows truthful without widening into missing helper-local parity or perf surfaces.
  * keep the roadmap-backed leaf-helper anchors explicit here too: `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c` stay the Phase 6 scope, and follow-through should remain limited to reminder-surface truthfulness, helper-local parity, or perf-gate drift inside that bounded packet rather than runtime-core or freeze-map targets.
Phase 8 notes
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/validate-phase8.py`
now keep the current Phase 8 docs-root reminder packet aligned to the shipped helper-first libbpf and command-surface evidence instead of collapsing the live packet back into broad userspace-adjacent claims.
  * keep the bounded current-`master` packet explicit through `tools/lib/subcmd/exec-cmd.zig`, `tools/lib/subcmd/help.zig`, `tools/lib/bpf/zigux_segments/verify.zig`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_perf_buffer_poll.zig`.
  * keep the smaller helper-local cursor and routing-summary packet explicit here too: `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` is landed current-`master` evidence below the still-deferred setup-side `perf-buffer-online-cpu-routing` boundary.
  * keep the deferred routing boundary honest from the docs root: do not present `/sys/devices/system/cpu/online`, cached `libbpf_num_possible_cpus()` sizing, online CPU filtering, per-CPU perf-event-array map updates, per-CPU `perf_event_open()` setup, perf-buffer ring `mmap()` setup, `PERF_EVENT_IOC_ENABLE` enablement, epoll-backed perf FD registration, or poll waits as landed Phase 8 behavior.
  * keep the bounded poll-helper review surface explicit too: `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `make -C zigux phase8-perf-buffer-poll-test`, and `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all` are current reminder surfaces inside the already-landed smaller helper packet.
  * keep the shared reminder companions aligned around `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `Documentation/zigux/phase8-tooling-lane-sequencing.md`, and reopen this docs-root summary only if one of those shared surfaces or the deeper boundary survey drifts again.
Phase 13 notes
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-shared-summary-guard-gap.md`
- `Documentation/zigux/phase13-notifier-summary-gap.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `zigux/tests/README.md`
now keep the current Phase 13 docs-root reminder packet explicit from the documentation root so the shared-subsystems lane stays tied to the roadmap's four shared-helper anchors instead of rebuilding the older validator-first or Makefile-route packet from missing companions.
  * keep the docs-root Phase 13 reminder packet grounded in the same four roadmap-backed anchors: `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c`.
  * keep the stable contributor-facing handle aligned through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `Documentation/zigux/phase13-release-coordination-matrix.md`, `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`, `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, and `zigux/tests/README.md` so the docs root matches the shipped shared-summary and tests-root alignment packet.
  * keep the shipped `libfs` packet explicit through `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json` instead of collapsing Phase 13 into docs-only workflow wording.
  * keep the narrower current-`master` `devres` packet explicit through `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `scripts/zigux/check-phase13-devres-dma-boundary.py`, `scripts/zigux/check-phase13-devres-mmio-packet.py`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig`, `zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`, `lib/devres_scatterlist.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist_build.zig` instead of rebuilding the older missing direct `lib/devres.zig` helper packet.
  * keep the shipped Landlock ownership, governance, slice, survey, ruleset replay, and syscall starter packet explicit through `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, and `zigux/tests/phase13_landlock_ruleset_manifest.json`, while keeping the direct Landlock syscall survey and replay companions in the repo-reality-gap bucket.
  * keep adjacent notifier evidence explicit through `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/bindings/notifier_abi.zig`, `include/zigux/abi.h`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, and `drivers/tty/hvc/hvc_console.h` without promoting that adjacent packet into a fifth shared-helper anchor.
  * current `master` does materialize `zigux/Makefile`, but it still does not materialize `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, so keep the returned file distinct from those still-missing Phase 13 route names instead of treating it as a shared build handle.
  * repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase13-libfs-slice.md`, `zigux/tests/phase13_libfs_addressability.zig`, `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check-phase13-devres-packet.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/validate-phase13-release.py`, `zigux/tests/phase13_build.zig`, `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, and `include/zigux/notifier_abi.h`, so keep those helper-local direct companions, validator-first helpers, build handles, and adjacent notifier helpers framed as repo-reality gaps rather than current docs-root evidence.
