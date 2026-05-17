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
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `zigux/tests/fixtures/phase1_helper_manifest.json`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase1-string-review-packet.py`
- `scripts/zigux/check-phase1-direct-owner-markers.py`
keep the live owner map, parked shared-replay-versus-direct-anchor split, and current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.
  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, closure-side, validator-first, bench, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence.
  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map and string-review guards: `scripts/zigux/check-phase1-string-review-packet.py` and `scripts/zigux/check-phase1-direct-owner-markers.py` are the shipped direct checks, while `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around them.
  * keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.
  * `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test` and `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.
Phase 2 notes
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/zig-toolchain-policy.json`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
now keep the current directly readable Phase 2 toolchain, kbuild, and kconfig bridge packet visible from the docs root instead of rebuilding the older closure-side validator stack from missing current-`master` paths.
  * repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `zigux/Makefile`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, so treat those closure-side, validator-first, cross-route, artifact-roster, and Linux-style make-route names as historical packet members until same-lane work rematerializes them on `master`.
  * keep the docs-root Phase 2 summary aligned to the shipped toolchain checker, the pinned toolchain policy, the surviving kbuild and alignment guards, the live `conf_bridge` plus `confdata_bridge` helpers, and the current kconfig fixture roster, without reviving missing closure, cross-target, artifact-tools, installer, or make-wrapper proof text.
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
- `python3 scripts/zigux/check-phase3-dev-t-starter-packet.py`
- `python3 scripts/zigux/check-phase3-errptr-xarray-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test`
now keep the current Phase 3 reminder surface anchored to one bounded `dev_t` starter packet with its directly readable export shim companion, one focused helper-local `err_ptr` / `xarray` slice, and one focused helper-local policy slice, instead of presenting the older broader validator, export/UAPI layout, catalog, low-level-wrapper, or shared replay packet as shipped docs-root evidence on current `master`.
  * the docs-root Phase 3 summary should keep the current starter packet explicit through `Documentation/zigux/phase3-abi-slice.md`, `Documentation/zigux/phase3-validator-support-surface.md`, `include/linux/zigux.h`, `include/zigux/dev_t.h`, `zigux/uapi/version.zig`, `zigux/uapi/dev_t.zig`, `zigux/bindings/abi.zig`, `zigux/bindings/dev_t.zig`, `zigux/bindings/version.zig`, `zigux/kernel/export_shim.zig`, `zigux/tests/phase3_dev_t_starter_packet.zig`, `zigux/tests/phase3_dev_t_starter_packet_build.zig`, `zigux/tests/phase3_dev_t_starter_packet_manifest.json`, and the dedicated `scripts/zigux/check-phase3-dev-t-starter-packet.py` checker, while the helper-local interop slice stays explicit through `Documentation/zigux/phase3-errptr-xarray-slice.md`, `zigux/helpers/err_ptr.zig`, `zigux/helpers/xa_value.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet.zig`, `zigux/tests/phase3_errptr_xarray_starter_packet_build.zig`, and `scripts/zigux/check-phase3-errptr-xarray-starter-packet.py`, and the focused policy slice stays explicit through `Documentation/zigux/phase3-policy-slice.md`, `include/zigux/abi.h`, `zigux/bindings/abi.zig`, `zigux/helpers/panic_policy.zig`, `zigux/helpers/allocator_policy.zig`, `zigux/helpers/unsafe_policy.zig`, `zigux/tests/phase3_policy_starter_packet.zig`, `zigux/tests/phase3_policy_starter_packet_build.zig`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, and `scripts/zigux/check-phase3-policy-starter-packet.py`.
  * keep broader routes such as `Documentation/zigux/phase3-abi-header-family-survey.md`, `Documentation/zigux/phase3-abi-h-boundary-next-step.md`, `zigux/bindings/notifier_abi.zig`, `zigux/tests/phase3_export_uapi_layout.zig`, `zigux/tests/phase3_export_uapi_layout_build.zig`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, and `scripts/zigux/phase3_catalog.py` framed as repo-reality gaps until fresh current-tree proof lands, while `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, `scripts/zigux/validate-phase3.py`, and `zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig` keep the current bounded atomic, barrier, and MMIO wrapper reminder packet explicit; keep `Documentation/zigux/phase3-shared-reminder-gap.md` explicit as the tracker for any remaining docs-root or tests-root reminder drift rather than reopening the stale saved Phase 3 publication packets.
Phase 5 notes
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `zigux/tests/README.md`
now keep the current shared Phase 5 reminder packet explicit from the docs root so contributor guidance still matches the four approved non-runtime sample anchors without inventing new sample behavior or runtime proof.
  * the docs-root Phase 5 summary should stay aligned with `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, and `zigux/tests/README.md`, and it should keep the same four roadmap-backed anchors explicit: `samples/kfifo/bytestream-example.c`, `samples/kobject/kobject-example.c`, `samples/kprobes/kretprobe_example.c`, and `samples/trace_events/trace-events-sample.c`.
  * keep the current sample-root proof truthful here too: `samples/zigux/bytestream_fifo.zig`, `samples/zigux/kobject_example.zig`, and `samples/zigux/kretprobe_example.zig` are the directly readable non-runtime sample-root ports on current `master`, while `samples/zigux/trace_events_string_formatting_sample.zig` is the bounded trace-events formatting companion rather than a fourth returned direct sample-root port or a fifth sample; keep the older direct trace-events sample-local companions and the shared `zigux/tests/phase5_build.zig` route framed only as repo-reality gaps or current public-tree-backed companion evidence until a fresh reread proves direct authenticated proof again.
  * keep the no-extra-sample boundaries explicit from this docs root too: there is no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` reference sample on current `master`, and the bounded `*string*` companion stays tied to the non-runtime trace-events anchor rather than helper-local delivery.
  * keep the Phase 5 versus Phase 9 boundary explicit: do not count `samples/zigux/runtime_*.zig` files as extra Phase 5 evidence, and do not widen this docs-root reminder into runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer claims while the freeze map keeps those later lanes separate.
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
- `scripts/zigux/check-phase13-tests-readme-alignment.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
now keep the current docs-root Phase 13 reminder packet explicit from the documentation root so contributor guidance stays tied to the shipped shared-summary guard, notifier gap note, tests-root alignment check, and the four roadmap-owned helper anchors instead of the older missing validator-first or Makefile-backed handle.
  * keep the shared contributor-facing handle explicit through `Documentation/zigux/phase13-contributor-workflow-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, and keep the shared-summary guard plus notifier gap notes explicit through `Documentation/zigux/phase13-shared-summary-guard-gap.md`, `Documentation/zigux/phase13-notifier-summary-gap.md`, and `scripts/zigux/check-phase13-tests-readme-alignment.py` while the active helper-local packet stays bounded to `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c`.
  * keep the shipped helper-local evidence explicit here too: `Documentation/zigux/phase13-libfs-survey.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_libfs_manifest.json`, `Documentation/zigux/phase13-devres-slice.md`, `Documentation/zigux/phase13-devres-survey.md`, `lib/devres.zig`, `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `Documentation/zigux/phase13-landlock-ruleset-ownership.md`, `Documentation/zigux/phase13-landlock-ruleset-slice.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/ruleset.zig`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` explicit, while `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `include/zigux/abi.h`, and `drivers/tty/hvc/hvc_console.h` stay adjacent notifier evidence rather than a fifth helper family.
  * current `master` still does not materialize `zigux/Makefile`, `make -C zigux phase13-validate`, `make -C zigux phase13`, `scripts/zigux/validate-phase13-release.py`, `scripts/zigux/check-phase13-devres-packet-alignment.py`, `scripts/zigux/check-phase13-landlock-ruleset-packet.py`, `scripts/zigux/check-phase13-notifier-priority-signal.py`, `scripts/zigux/check-phase13-shared-summary-surfaces.py`, `Documentation/zigux/phase13-notifier-list-survey.md`, `zigux/tests/phase13_build.zig`, `zigux/tests/phase13_libfs_addressability.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check-phase13-notifier-packet.py`, `include/zigux/notifier_abi.h`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig`, so keep those routes and companions framed as repo-reality gaps instead of direct current-`master` docs-root evidence.
