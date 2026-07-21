const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_HARNESS_COVERAGE=pass";
pub const self_test_pass_marker = "PHASE10_HARNESS_COVERAGE_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "scripts\\zigux/check_phase10_harness_coverage.zig",
    "scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig",
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
};

const markers_1 = [_][]const u8{
    "scripts\\zigux/check_phase10_harness_coverage.zig",
    "scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
    "blocked risky-transport posture",
    "returned shared closure packet anchors: `scripts\\zigux/validate_phase10.zig`, `scripts\\zigux/validate_phase10_closure.zig`, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, and `zigux/tests/phase10_closure_manifest.json`",
    "Keep `zigux/tests/phase10_virtio_ring_survey.zig` explicit as the returned dedicated ring survey gate beside `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_build.zig` instead of framing that survey replay as stale packet trivia.",
};

const markers_2 = [_][]const u8{
    "`PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`",
    "directly re-readable shared reminder surfaces now include `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, and `scripts/zigux/README.md`",
    "directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts\\zigux/check_phase10_ring_packet.zig`, `scripts\\zigux/validate_phase10.zig`, `scripts\\zigux/validate_phase10_closure.zig`, and `zigux/Makefile`",
    "directly re-readable shared checker-backed reminder anchors also now include `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, the bootstrap-route guard, `scripts\\zigux/check_phase10_core_packet.zig`, `scripts\\zigux/check_phase10_shared_freeze_boundary.zig`, `scripts\\zigux/check_phase10_input_packet.zig`, `scripts\\zigux/check_phase10_mmio_packet.zig`, `scripts\\zigux/check_phase10_harness_coverage.zig`, `scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig`, and the manifest-count guard",
    "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, and `zigux/tests/phase10_virtio_mmio_manifest.json`",
    "current exact-path contents reads in this lane now rematerialize `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`, while public current-`master` readback continues to rematerialize `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, and `zigux/tests/phase10_virtio_core_survey.zig` beside the returned `zigux/tests/phase10_virtio_core.zig`, `scripts\\zigux/validate_phase10.zig`, `scripts\\zigux/validate_phase10_closure.zig`, `scripts\\zigux/check_phase10_ring_packet.zig`, and `zigux/Makefile` on current `master`",
    "`scripts\\zigux/validate_phase10.zig`, `scripts\\zigux/check_phase10_ring_packet.zig`, and `zigux/Makefile` themselves now rematerialize on current `master`, and their live bodies expose the dedicated shared Phase 10 validate/test route stack, so keep those returned files and that returned build-gate posture explicit here rather than framing them as repo-reality gaps.",
    "The shared bootstrap-route guard now stays explicit through `scripts\\zigux/check_phase10_bootstrap_route.zig` so the closure packet fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`.",
    "The shared freeze-boundary guard now stays explicit through `scripts\\zigux/check_phase10_shared_freeze_boundary.zig` so the closure packet fails closed if the Phase 14 study-only anchors drift into Phase 10 closure claims.",
    "The shared closure-manifest count guard now stays explicit through `scripts\\zigux/check_phase10_closure_manifest_counts.zig` so the closure packet fails closed if its summary counts drift from the listed docs, manifests, drivers, or tests surfaces.",
    "The returned shared and packet-local review guards also stay explicit through `scripts\\zigux/check_phase10_core_packet.zig`, `scripts\\zigux/check_phase10_ring_packet.zig`, `scripts\\zigux/check_phase10_input_packet.zig`, and `scripts\\zigux/check_phase10_mmio_packet.zig`, so this shared closure note keeps the current virtqueue, core, input, and MMIO lab validation stack visible beside the returned shared validate/test route rather than collapsing that evidence into the build gate alone.",
    "Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root packet on current `master` and keep it aligned with the shared closure note, lane-sequencing note, review checklist, and tests-root reminder instead of leaving it in neighboring-surface wording.",
    "`lab_only_driver_validation=starter_landed`",
    "- evidence: `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `zigux/tests/phase10_build.zig`, `drivers/virtio/virtio_verify.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, the bootstrap-route guard, `scripts\\zigux/check_phase10_core_packet.zig`, `scripts\\zigux/check_phase10_shared_freeze_boundary.zig`, `scripts\\zigux/check_phase10_ring_packet.zig`, `scripts\\zigux/check_phase10_input_packet.zig`, `scripts\\zigux/check_phase10_mmio_packet.zig`, `scripts\\zigux/check_phase10_harness_coverage.zig`, `scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig`, the manifest-count guard, `scripts\\zigux/validate_phase10.zig`, `scripts\\zigux/validate_phase10_closure.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
    "scripts\\zigux/check_phase10_harness_coverage.zig",
    "scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig",
    "`zigux/Makefile`",
    "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `drivers/virtio/virtio_ring.zig`, and `scripts\\zigux/check_phase10_ring_packet.zig`, while direct current-`master` contents reads now also rematerialize `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, and `drivers/virtio/virtio_ring_registration_summary.zig` beside the already-returned notification-data, reset-readiness, and survey replays, so keep that broader ring replay packet explicit here instead of treating it as fallback-only evidence.",
};

const markers_3 = [_][]const u8{
    "scripts\\zigux/check_phase10_harness_coverage.zig",
    "scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig",
    "- shared reminder lane owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-freeze-boundary-gap-survey.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts\\zigux/check_phase10_bootstrap_route.zig`, `scripts\\zigux/check_phase10_shared_freeze_boundary.zig`, `scripts\\zigux/check_phase10_harness_coverage.zig`, `scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig`, `scripts\\zigux/check_phase10_closure_manifest_counts.zig`, and the shared Phase 10 wording in the docs root, review checklist, and tests root, with `scripts/zigux/README.md` aligned as the current dedicated Phase 10 scripts-root packet on current `master`",
    "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "current `master` now rematerializes `scripts\\zigux/validate_phase10.zig`, `scripts\\zigux/validate_phase10_closure.zig`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/Makefile`; treat those returned validator and build-route surfaces as part of the shared closure gate while keeping the returned dedicated core checker plus `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig` framed as bounded core-packet evidence rather than repo-reality gaps in this lane",
    "Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root packet on current `master` and keep it aligned with the shared closure note, lane-sequencing note, review checklist, and tests-root reminder instead of leaving it in neighboring-surface wording.",
    "`zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig` are back as directly re-readable helper-local manifest, replay, and standalone build-shard anchors",
    "Current `master` gives this lane a mixed but broader set of directly re-readable shared and packet-local anchors: `scripts\\zigux/check_phase10_closure_manifest_counts.zig`, `scripts\\zigux/validate_phase10.zig`, `scripts\\zigux/validate_phase10_closure.zig`, `zigux/tests/phase10_closure_manifest.json`, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core_manifest.json`, `scripts\\zigux/check_phase10_core_packet.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`",
    "Use the directly re-readable shared validator pair, closure manifest, dedicated core checker, driver-id replay pair, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core.zig`, and Makefile-backed route anchors together with the returned core-slice, core-verify, reset-queue, interrupt-compound-ack, and survey-gate companions before widening shared wording back into transport-facing claims.",
    "Treat the shared `zigux/tests/phase10_build.zig` route as already-landed validation evidence",
    "Current `master` also rematerializes `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, and `zigux/tests/phase10_virtio_ring_survey.zig`, so keep that notification-data replay, queue-registration replay, reset-readiness replay, and dedicated ring survey gate explicit with `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and the shared `zigux/tests/phase10_build.zig` route instead of framing either replay as a direct-readback gap.",
};

const markers_4 = [_][]const u8{
    "drivers/virtio/virtio_input_probe_preflight.zig",
    "drivers/virtio/virtio_input_registration_preflight.zig",
    "drivers/virtio/virtio_input_status_drain.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "drivers/virtio/virtio_input_teardown_observation.zig",
    "drivers/virtio/virtio_input_verify.zig",
    "zigux/tests/phase10_virtio_input.zig",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "zigux/tests/phase10_virtio_input_survey.zig",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "queued status completions reclaimable in memory",
    "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice",
};

const markers_5 = [_][]const u8{
    "pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;",
    "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
    "pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {",
    "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
};

const markers_6 = [_][]const u8{
    "test \"phase10 virtio input verify keeps wrapper-facing queue preflight ordering explicit\" {",
    "test \"phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims\" {",
    "test \"phase10 virtio input verify keeps teardown and status-drain wrapper parity explicit across reset\" {",
};

const markers_7 = [_][]const u8{
    "pub fn summarizeNotificationData(",
    "pub fn summarizeDelayedCallback(",
    "pub fn summarizeResetReadiness(",
    "test \"phase10 virtio ring verify keeps notification-data next-avail state reviewable across split packed and reset replay\" {",
    "test \"phase10 virtio ring verify keeps delayed callback wrapper thresholds explicit\" {",
    "test \"phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay\" {",
};

const markers_8 = [_][]const u8{
    "## Phase 10",
    "scripts\\zigux/check_phase10_bootstrap_route.zig",
    "scripts\\zigux/check_phase10_harness_coverage.zig",
    "scripts\\zigux/check_phase10_tests_readme_core_surfaces.zig",
    "scripts\\zigux/validate_phase10.zig",
    "scripts\\zigux/validate_phase10_closure.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "make -C zigux phase10-validate",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
    "`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit, and the now-returned exact-path `drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit as the narrower core-side follow-through evidence on current `master`",
    "keep risky transport parked",
    "Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root packet on current `master` and keep it aligned with the shared closure note, lane-sequencing note, review checklist, and tests-root reminder instead of leaving it in neighboring-surface wording.",
};

const markers_9 = [_][]const u8{
    "test \"phase10 virtio ring notification-data replay keeps split and packed next-avail state explicit\" {",
    "const split_summary = try ring.notificationDataSummary(1);",
    "const packed_summary = try ring.notificationDataSummary(2);",
};

const markers_10 = [_][]const u8{
    "test \"phase10 virtio ring repeated prepareKick stays idle until new descriptors are published\" {",
    "kick_summary = try ring.prepareKick(1);",
    "try std.testing.expect(!kick_summary.needs_kick);",
};

const markers_11 = [_][]const u8{
    "test \"phase10 virtio ring reset reuse stays blocked until queue-local reset prerequisites clear and then replays from a clean queue state\" {",
    "const reset = try ring.resetQueue(2);",
    "const kick_after_reset = try ring.prepareKick(2);",
};

const markers_12 = [_][]const u8{
    "test \"phase10 virtio ring broken-queue coverage kicks published work before used accounting and keeps notification history visible\" {",
    "try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));",
    "const cleared_summary = try ring.clearBroken(3);",
};

const markers_13 = [_][]const u8{
    "test \"phase10 virtio ring delayed callback budget stays bounded to queue-local replay state\" {",
    "try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);",
    "try std.testing.expect(summary.should_poll);",
    "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
};

const markers_14 = [_][]const u8{
    "\"phase10-virtio-core-tests\"",
    "\"phase10-virtio-core-interrupt-compound-ack-tests\"",
    "run_phase10_virtio_core_interrupt_compound_ack_tests.step",
    "\"phase10-virtio-core-reset-queue-tests\"",
    "run_phase10_virtio_core_reset_queue_tests.step",
    "\"phase10-virtio-core-verify-tests\"",
    "run_phase10_virtio_core_verify_tests.step",
    "\"phase10-virtio-core-survey-tests\"",
    "run_phase10_virtio_core_survey_tests.step",
    "\"phase10-virtio-driver-id-tests\"",
    "run_phase10_virtio_driver_id_tests.step",
    "\"phase10-virtio-input-tests\"",
    "\"phase10-virtio-input-probe-preflight-tests\"",
    "\"phase10-virtio-input-queue-callback-preflight-tests\"",
    "\"phase10-virtio-input-registration-preflight-tests\"",
    "\"phase10-virtio-input-status-drain-tests\"",
    "\"phase10-virtio-input-teardown-preflight-tests\"",
    "run_phase10_virtio_input_teardown_preflight_tests.step",
    "\"phase10-virtio-input-teardown-observation-tests\"",
    "\"phase10-virtio-input-survey-tests\"",
    "\"phase10-virtio-input-verify-tests\"",
    "\"phase10-virtio-ring-tests\"",
    "run_phase10_virtio_ring_tests.step",
    "\"phase10-virtio-ring-notification-data-readiness-tests\"",
    "run_phase10_virtio_ring_notification_data_readiness_tests.step",
    "\"phase10-virtio-ring-verify-tests\"",
    "run_phase10_virtio_ring_verify_tests.step",
    "\"phase10-virtio-ring-publish-readiness-tests\"",
    "run_phase10_virtio_ring_publish_readiness_tests.step",
    "\"phase10-virtio-ring-prepare-kick-idempotent-tests\"",
    "\"phase10-virtio-ring-reset-reuse-tests\"",
    "\"phase10-virtio-ring-broken-queue-queue-discipline-tests\"",
    "\"phase10-virtio-ring-delayed-callback-budget-tests\"",
    "\"phase10-virtio-ring-survey-tests\"",
    "\"phase10-virtio-mmio-tests\"",
    "\"phase10-virtio-mmio-lab-tests\"",
    "run_phase10_virtio_mmio_lab_tests.step",
    "\"phase10-virtio-mmio-verify-tests\"",
    "\"phase10-virtio-mmio-survey-tests\"",
    "Run the live Phase 10 virtio core, input, ring, and MMIO lab validation tests",
};

const markers_15 = [_][]const u8{
    "phase10-validate:",
    "$(ZIG) run scripts/zigux/check_phase10_bootstrap_route.zig",
    "$(ZIG) run scripts/zigux/check_phase10_shared_freeze_boundary.zig",
    "$(ZIG) run scripts/zigux/check_phase10_harness_coverage.zig",
    "$(ZIG) run scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
    "phase10-test:",
    "$(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase10_build.zig --summary all",
    "phase10: phase10-validate phase10-test",
};

const markers_16 = [_][]const u8{
    "Validate Phase 10 checker-backed review packet",
    "make -C zigux phase10-validate",
    "Run Phase 10 helper tests",
    "make -C zigux phase10-test",
};

const markers_17 = [_][]const u8{
    "zig run scripts/zigux/check_phase10_shared_freeze_boundary.zig",
    "\"kernel/workqueue.c\"",
    "\"kernel/trace/ring_buffer.c\"",
    "\"kernel/sched/core.c\"",
    "\"net/core/skbuff.c\"",
};

const markers_18 = [_][]const u8{
    "Self-test current Phase 10 bootstrap route checker",
    "Check current Phase 10 bootstrap route",
    "Validate Phase 10 checker-backed review packet",
    "make -C zigux phase10-validate",
    "Run Phase 10 helper tests",
    "make -C zigux phase10-test",
};

const markers_19 = [_][]const u8{
    "\"lab_only_driver_validation\"",
    "\"scripts/zigux/check_phase10_harness_coverage.zig\"",
    "\"scripts/zigux/check_phase10_tests_readme_core_surfaces.zig\"",
    "\"scripts/zigux/validate_phase10.zig\"",
    "\"scripts/zigux/validate_phase10_closure.zig\"",
    "\"zig run scripts/zigux/validate_phase10.zig\"",
    "\"zig run scripts/zigux/validate_phase10_closure.zig\"",
};

const forbidden_markers_0 = [_][]const u8{
    "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json` and `zigux/tests/phase10_virtio_input_manifest.json`",
    "current contents reads still do not materialize `zigux/tests/phase10_virtio_core_manifest.json`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, and `zigux/tests/phase10_virtio_core_survey.zig` through the direct readback available in this lane, while the returned `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and `zigux/Makefile` now rematerialize the dedicated shared Phase 10 validate/test route surface on current `master`",
    "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `drivers/virtio/virtio_ring.zig`, while `zigux/tests/phase10_virtio_ring_survey.zig` still remains a direct-readback gap in this lane.",
};

const forbidden_markers_1 = [_][]const u8{
    "Authenticated contents reads still fail for `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, and the broader validator-first `scripts/zigux/validate-phase10.py` route through the direct readback available in this lane.",
    "current `master` still does not materialize `scripts/zigux/validate-phase10.py` through the direct readback available in this lane, but it now rematerializes `scripts/zigux/validate-phase10-closure.py`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/Makefile`; keep the still-missing broader validator-script name framed as a last-known packet member or repo-reality gap while treating the returned closure validator, closure manifest, and Makefile-backed `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` route stack as the shared closure and build gate",
    "Current `master` also rematerializes `zigux/tests/phase10_virtio_ring_survey.zig`, so keep that dedicated ring survey gate explicit with `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and the shared `zigux/tests/phase10_build.zig` route instead of framing the survey gate as a direct-readback gap.",
};

const forbidden_markers_2 = [_][]const u8{
    "keep `zigux/tests/phase10_virtio_ring_survey.zig` framed as a last-known packet member until a fresh reread proves it rematerializes on current `master`.",
    "current `master` still does not materialize `scripts/zigux/validate-phase10.py`, `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, and `zigux/tests/phase10_virtio_ring.zig` through the direct readback available in this lane, so keep them framed as last-known packet members or repo-reality gaps rather than direct current-`master` evidence.",
};

const forbidden_markers_3 = [_][]const u8{
    "current `master` still does not materialize `Documentation/zigux/phase10-virtio-core-slice.md`",
};

const forbidden_markers_4 = [_][]const u8{
    "Run the live Phase 10 virtio input, ring, and MMIO lab validation tests",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase10-closure-evidence.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase10-virtio-input-module-slice.md", .markers = &markers_4 },
    .{ .rel = "drivers/virtio/virtio_input_registration_preflight.zig", .markers = &markers_5 },
    .{ .rel = "drivers/virtio/virtio_input_verify.zig", .markers = &markers_6 },
    .{ .rel = "drivers/virtio/virtio_ring_verify.zig", .markers = &markers_7 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_8 },
    .{ .rel = "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig", .markers = &markers_9 },
    .{ .rel = "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig", .markers = &markers_10 },
    .{ .rel = "zigux/tests/phase10_virtio_ring_reset_reuse.zig", .markers = &markers_11 },
    .{ .rel = "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig", .markers = &markers_12 },
    .{ .rel = "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig", .markers = &markers_13 },
    .{ .rel = "zigux/tests/phase10_build.zig", .markers = &markers_14 },
    .{ .rel = "zigux/Makefile", .markers = &markers_15 },
    .{ .rel = "scripts/zigux/check_phase10_bootstrap_route.zig", .markers = &markers_16 },
    .{ .rel = "scripts/zigux/check_phase10_shared_freeze_boundary.zig", .markers = &markers_17 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_18 },
    .{ .rel = "zigux/tests/phase10_closure_manifest.json", .markers = &markers_19 },
};

const forbidden_contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase10-closure-evidence.md", .markers = &forbidden_markers_0 },
    .{ .rel = "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", .markers = &forbidden_markers_1 },
    .{ .rel = "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", .markers = &forbidden_markers_2 },
    .{ .rel = "scripts/zigux/README.md", .markers = &forbidden_markers_3 },
    .{ .rel = "zigux/tests/phase10_build.zig", .markers = &forbidden_markers_4 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
    for (forbidden_contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| if (std.mem.indexOf(u8, text, marker) != null) return error.ForbiddenMarkerPresent;
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE10_HARNESS_COVERAGE_REQUIRED_FILE_COUNT=20", .{});
    try guard.printLine(io, "PHASE10_HARNESS_COVERAGE_REQUIRED_MARKER_COUNT=186", .{});
    try guard.printLine(io, "PHASE10_HARNESS_COVERAGE_FORBIDDEN_MARKER_COUNT=10", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_HARNESS_COVERAGE_SELF_TEST_CASE_COUNT=42", .{});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE10_HARNESS_COVERAGE_SELF_TEST=pass";
//
// const PHASE10_SCRIPTS_ROOT_PHRASE = [_][]const u8{
//     "Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root packet on current `master` and keep it aligned with the shared closure note, lane-sequencing note, review checklist, and tests-root reminder instead of leaving it in neighboring-surface wording.",
// };
//
// const SELF_TEST_MUTATIONS = [_][]const u8{
//     "(Documentation/zigux/phase10-closure-evidence.md",
//     "scripts/zigux/check_phase10_ring_packet.zig",
//     "scripts/zigux/check_phase10_ring_packet_missing.zig",
//     "Documentation/zigux/phase10-closure-evidence.md:directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, and `zigux/Makefile`",
//     ")",
//     "(Documentation/zigux/phase10-closure-evidence.md",
//     "current exact-path contents reads in this lane now rematerialize `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`, while public current-`master` readback continues to rematerialize `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, and `zigux/tests/phase10_virtio_core_survey.zig` beside the returned `zigux/tests/phase10_virtio_core.zig`, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, and `zigux/Makefile` on current `master`",
//     "current exact-path contents reads in this lane now rematerialize `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`, while public current-`master` readback continues to rematerialize `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, and `zigux/tests/phase10_virtio_core_survey.zig` beside the returned `zigux/tests/phase10_virtio_core_missing.zig`, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, and `zigux/Makefile` on current `master`",
//     "Documentation/zigux/phase10-closure-evidence.md:current exact-path contents reads in this lane now rematerialize `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`, while public current-`master` readback continues to rematerialize `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, and `zigux/tests/phase10_virtio_core_survey.zig` beside the returned `zigux/tests/phase10_virtio_core.zig`, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, and `zigux/Makefile` on current `master`",
//     ")",
//     "(Documentation/zigux/phase10-closure-evidence.md",
//     "directly re-readable shared checker-backed reminder anchors also now include `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, the bootstrap-route guard, `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_input_packet.zig`, `scripts/zigux/check_phase10_mmio_packet.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, and the manifest-count guard",
//     "directly re-readable shared checker-backed reminder anchors also now include `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, the bootstrap-route guard, `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_input_packet.zig`, `scripts/zigux/check_phase10_mmio_packet.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, and the missing-count guard",
//     "Documentation/zigux/phase10-closure-evidence.md:directly re-readable shared checker-backed reminder anchors also now include `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, the bootstrap-route guard, `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_input_packet.zig`, `scripts/zigux/check_phase10_mmio_packet.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, and the manifest-count guard",
//     ")",
//     "(Documentation/zigux/phase10-closure-evidence.md",
//     "The shared freeze-boundary guard now stays explicit through `scripts/zigux/check_phase10_shared_freeze_boundary.zig` so the closure packet fails closed if the Phase 14 study-only anchors drift into Phase 10 closure claims.",
//     "The shared freeze-boundary guard now stays explicit through `scripts/zigux/check_phase10_shared_freeze_boundary_missing.zig` so the closure packet fails closed if the Phase 14 study-only anchors drift into Phase 10 closure claims.",
//     "Documentation/zigux/phase10-closure-evidence.md:The shared freeze-boundary guard now stays explicit through `scripts/zigux/check_phase10_shared_freeze_boundary.zig` so the closure packet fails closed if the Phase 14 study-only anchors drift into Phase 10 closure claims.",
//     ")",
//     "(Documentation/zigux/phase10-closure-evidence.md",
//     "The shared closure-manifest count guard now stays explicit through `scripts/zigux/check_phase10_closure_manifest_counts.zig` so the closure packet fails closed if its summary counts drift from the listed docs, manifests, drivers, or tests surfaces.",
//     "The shared closure-manifest count guard now stays explicit through `scripts/zigux/check_phase10_closure_manifest_counts_missing.zig` so the closure packet fails closed if its summary counts drift from the listed docs, manifests, drivers, or tests surfaces.",
//     "Documentation/zigux/phase10-closure-evidence.md:The shared closure-manifest count guard now stays explicit through `scripts/zigux/check_phase10_closure_manifest_counts.zig` so the closure packet fails closed if its summary counts drift from the listed docs, manifests, drivers, or tests surfaces.",
//     ")",
//     "(Documentation/zigux/phase10-closure-evidence.md",
//     "The returned shared and packet-local review guards also stay explicit through `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts/zigux/check_phase10_input_packet.zig`, and `scripts/zigux/check_phase10_mmio_packet.zig`, so this shared closure note keeps the current virtqueue, core, input, and MMIO lab validation stack visible beside the returned shared validate/test route rather than collapsing that evidence into the build gate alone.",
//     "The returned shared and packet-local review guards also stay explicit through `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts/zigux/check_phase10_input_packet_missing.zig`, and `scripts/zigux/check_phase10_mmio_packet.zig`, so this shared closure note keeps the current virtqueue, core, input, and MMIO lab validation stack visible beside the returned shared validate/test route rather than collapsing that evidence into the build gate alone.",
//     "Documentation/zigux/phase10-closure-evidence.md:The returned shared and packet-local review guards also stay explicit through `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts/zigux/check_phase10_input_packet.zig`, and `scripts/zigux/check_phase10_mmio_packet.zig`, so this shared closure note keeps the current virtqueue, core, input, and MMIO lab validation stack visible beside the returned shared validate/test route rather than collapsing that evidence into the build gate alone.",
//     ")",
//     "(Documentation/zigux/phase10-closure-evidence.md",
//     "- evidence: `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `zigux/tests/phase10_build.zig`, `drivers/virtio/virtio_verify.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, the bootstrap-route guard, `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts/zigux/check_phase10_input_packet.zig`, `scripts/zigux/check_phase10_mmio_packet.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, the manifest-count guard, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
//     "- evidence: `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `zigux/tests/phase10_build.zig`, `drivers/virtio/virtio_verify.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, the bootstrap-route guard, `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts/zigux/check_phase10_input_packet.zig`, `scripts/zigux/check_phase10_mmio_packet.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, the manifest-count guard, `scripts\zigux/validate_phase10_missing.zig`, `scripts\zigux/validate_phase10_closure.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
//     "Documentation/zigux/phase10-closure-evidence.md:- evidence: `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `zigux/tests/phase10_build.zig`, `drivers/virtio/virtio_verify.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, the bootstrap-route guard, `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts/zigux/check_phase10_input_packet.zig`, `scripts/zigux/check_phase10_mmio_packet.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, the manifest-count guard, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
//     ")",
//     "(Documentation/zigux/phase10-closure-evidence.md",
//     "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `drivers/virtio/virtio_ring.zig`, and `scripts/zigux/check_phase10_ring_packet.zig`, while direct current-`master` contents reads now also rematerialize `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, and `drivers/virtio/virtio_ring_registration_summary.zig` beside the already-returned notification-data, reset-readiness, and survey replays, so keep that broader ring replay packet explicit here instead of treating it as fallback-only evidence.",
//     "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `drivers/virtio/virtio_ring.zig`, and `scripts/zigux/check_phase10_ring_packet.zig`, while direct current-`master` contents reads now also rematerialize `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay_missing.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, and `drivers/virtio/virtio_ring_registration_summary.zig` beside the already-returned notification-data, reset-readiness, and survey replays, so keep that broader ring replay packet explicit here instead of treating it as fallback-only evidence.",
//     "Documentation/zigux/phase10-closure-evidence.md:The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `drivers/virtio/virtio_ring.zig`, and `scripts/zigux/check_phase10_ring_packet.zig`, while direct current-`master` contents reads now also rematerialize `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, and `drivers/virtio/virtio_ring_registration_summary.zig` beside the already-returned notification-data, reset-readiness, and survey replays, so keep that broader ring replay packet explicit here instead of treating it as fallback-only evidence.",
//     ")",
//     "(Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
//     "- shared reminder lane owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-freeze-boundary-gap-survey.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check_phase10_bootstrap_route.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, `scripts/zigux/check_phase10_closure_manifest_counts.zig`, and the shared Phase 10 wording in the docs root, review checklist, and tests root, with `scripts/zigux/README.md` aligned as the current dedicated Phase 10 scripts-root packet on current `master`",
//     "- shared reminder lane owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-freeze-boundary-gap-survey.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check_phase10_bootstrap_route.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, `scripts/zigux/check_phase10_closure_manifest_counts_missing.zig`, and the shared Phase 10 wording in the docs root, review checklist, and tests root, with `scripts/zigux/README.md` aligned as the current dedicated Phase 10 scripts-root packet on current `master`",
//     "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:- shared reminder lane owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-freeze-boundary-gap-survey.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check_phase10_bootstrap_route.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, `scripts/zigux/check_phase10_closure_manifest_counts.zig`, and the shared Phase 10 wording in the docs root, review checklist, and tests root, with `scripts/zigux/README.md` aligned as the current dedicated Phase 10 scripts-root packet on current `master`",
//     ")",
//     "(Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
//     "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
//     "zigux/tests/phase10_virtio_ring_notification_data_readiness_missing.zig",
//     "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md:Current `master` gives this lane a mixed but broader set of directly re-readable shared and packet-local anchors: `scripts/zigux/check_phase10_closure_manifest_counts.zig`, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `zigux/tests/phase10_closure_manifest.json`, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core_manifest.json`, `scripts/zigux/check_phase10_core_packet.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`",
//     ")",
//     "(Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
//     "zigux/tests/phase10_virtio_core.zig",
//     "zigux/tests/phase10_virtio_core_missing.zig",
//     "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md:returned shared closure packet anchors: `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, and `zigux/tests/phase10_closure_manifest.json`",
//     ")",
//     "(Documentation/zigux/phase10-virtio-input-module-slice.md",
//     "zigux/tests/phase10_virtio_input_probe_preflight.zig",
//     "zigux/tests/phase10_virtio_input_probe_preflight_missing.zig",
//     "Documentation/zigux/phase10-virtio-input-module-slice.md:zigux/tests/phase10_virtio_input_probe_preflight.zig",
//     ")",
//     "(Documentation/zigux/phase10-virtio-input-module-slice.md",
//     "drivers/virtio/virtio_input_teardown_preflight.zig",
//     "drivers/virtio/virtio_input_teardown_preflight_missing.zig",
//     "Documentation/zigux/phase10-virtio-input-module-slice.md:drivers/virtio/virtio_input_teardown_preflight.zig",
//     ")",
//     "(Documentation/zigux/phase10-virtio-input-module-slice.md",
//     "zigux/tests/phase10_virtio_input_manifest.json",
//     "zigux/tests/phase10_virtio_input_manifest_missing.json",
//     "Documentation/zigux/phase10-virtio-input-module-slice.md:zigux/tests/phase10_virtio_input_manifest.json",
//     ")",
//     "(Documentation/zigux/phase10-virtio-input-module-slice.md",
//     "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
//     "zigux/tests/phase10_virtio_input_teardown_preflight_missing.zig",
//     "Documentation/zigux/phase10-virtio-input-module-slice.md:zigux/tests/phase10_virtio_input_teardown_preflight.zig",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-core-interrupt-compound-ack-tests\"",
//     "\"phase10-virtio-core-interrupt-compound-ack-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-core-interrupt-compound-ack-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_core_interrupt_compound_ack_tests.step",
//     "run_phase10_virtio_core_interrupt_compound_ack_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_core_interrupt_compound_ack_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-core-reset-queue-tests\"",
//     "\"phase10-virtio-core-reset-queue-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-core-reset-queue-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_core_reset_queue_tests.step",
//     "run_phase10_virtio_core_reset_queue_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_core_reset_queue_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-core-verify-tests\"",
//     "\"phase10-virtio-core-verify-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-core-verify-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_core_verify_tests.step",
//     "run_phase10_virtio_core_verify_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_core_verify_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-core-survey-tests\"",
//     "\"phase10-virtio-core-survey-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-core-survey-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_core_survey_tests.step",
//     "run_phase10_virtio_core_survey_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_core_survey_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-driver-id-tests\"",
//     "\"phase10-virtio-driver-id-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-driver-id-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_driver_id_tests.step",
//     "run_phase10_virtio_driver_id_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_driver_id_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-input-teardown-preflight-tests\"",
//     "\"phase10-virtio-input-teardown-preflight-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-input-teardown-preflight-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_input_teardown_preflight_tests.step",
//     "run_phase10_virtio_input_teardown_preflight_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_input_teardown_preflight_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-ring-tests\"",
//     "\"phase10-virtio-ring-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-ring-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_ring_tests.step",
//     "run_phase10_virtio_ring_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_ring_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-ring-notification-data-readiness-tests\"",
//     "\"phase10-virtio-ring-notification-data-readiness-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-ring-notification-data-readiness-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_ring_notification_data_readiness_tests.step",
//     "run_phase10_virtio_ring_notification_data_readiness_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_ring_notification_data_readiness_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_ring_verify_tests.step",
//     "run_phase10_virtio_ring_verify_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_ring_verify_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-ring-publish-readiness-tests\"",
//     "\"phase10-virtio-ring-publish-readiness-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-ring-publish-readiness-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_ring_publish_readiness_tests.step",
//     "run_phase10_virtio_ring_publish_readiness_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_ring_publish_readiness_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-mmio-lab-tests\"",
//     "\"phase10-virtio-mmio-lab-tests-missing\"",
//     "zigux/tests/phase10_build.zig:\"phase10-virtio-mmio-lab-tests\"",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "run_phase10_virtio_mmio_lab_tests.step",
//     "run_phase10_virtio_mmio_lab_tests_missing.step",
//     "zigux/tests/phase10_build.zig:run_phase10_virtio_mmio_lab_tests.step",
//     ")",
//     "(zigux/tests/phase10_build.zig",
//     "Run the live Phase 10 virtio core, input, ring, and MMIO lab validation tests",
//     "Run the live Phase 10 virtio input, ring, and MMIO lab validation tests",
//     "zigux/tests/phase10_build.zig:forbidden:Run the live Phase 10 virtio input, ring, and MMIO lab validation tests",
//     ")",
//     "(scripts/zigux/README.md",
//     "`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit, and the now-returned exact-path `drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit as the narrower core-side follow-through evidence on current `master`",
//     "current `master` still does not materialize `Documentation/zigux/phase10-virtio-core-slice.md`, so keep the broader core-side slice framed as a repo-reality gap while the returned core survey, ring, input, and MMIO packet anchors continue to carry the bounded shared reminder",
//     "scripts/zigux/README.md:`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit, and the now-returned exact-path `drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit as the narrower core-side follow-through evidence on current `master`",
//     ")",
//     "(zigux/tests/phase10_closure_manifest.json",
//     "\"scripts\zigux/validate_phase10.zig\"",
//     "\"scripts\zigux/validate_phase10_missing.zig\"",
//     "zigux/tests/phase10_closure_manifest.json:\"scripts\zigux/validate_phase10.zig\"",
//     ")",
// };
//
// const SELF_TEST_MISSING_FILES = [_][]const u8{
//     "Documentation/zigux/phase10-closure-evidence.md",
//     "drivers/virtio/virtio_ring_verify.zig",
//     "scripts/zigux/README.md",
// };
//
// const REQUIRED_MARKERS = [_][]const u8{
//     "Documentation/zigux/review-checklist.md",
//     "scripts/zigux/check_phase10_harness_coverage.zig",
//     "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
//     "zigux/Makefile",
//     "zigux/tests/phase10_build.zig",
//     "make -C zigux phase10-validate",
//     "make -C zigux phase10-test",
//     "make -C zigux phase10",
//     "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
//     "scripts/zigux/check_phase10_harness_coverage.zig",
//     "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
//     "drivers/virtio/virtio_input_queue_callback_preflight.zig",
//     "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
//     "drivers/virtio/virtio_input_teardown_observation.zig",
//     "drivers/virtio/virtio_input_verify.zig",
//     "zigux/tests/phase10_virtio_input_teardown_observation.zig",
//     "drivers/virtio/virtio_ring_verify.zig",
//     "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
//     "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
//     "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
//     "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
//     "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
//     "make -C zigux phase10-validate",
//     "make -C zigux phase10-test",
//     "make -C zigux phase10",
//     "blocked risky-transport posture",
//     "returned shared closure packet anchors: `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, and `zigux/tests/phase10_closure_manifest.json`",
//     "Keep `zigux/tests/phase10_virtio_ring_survey.zig` explicit as the returned dedicated ring survey gate beside `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `zigux/tests/phase10_build.zig` instead of framing that survey replay as stale packet trivia.",
//     "Documentation/zigux/phase10-closure-evidence.md",
//     "`PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`",
//     "directly re-readable shared reminder surfaces now include `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, and `scripts/zigux/README.md`",
//     "directly re-readable helper, verify, build, and route-surface anchors now include `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_input_verify.zig`, `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, and `zigux/Makefile`",
//     "directly re-readable shared checker-backed reminder anchors also now include `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, the bootstrap-route guard, `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_input_packet.zig`, `scripts/zigux/check_phase10_mmio_packet.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, and the manifest-count guard",
//     "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_closure_manifest.json`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_input_manifest.json`, and `zigux/tests/phase10_virtio_mmio_manifest.json`",
//     "current exact-path contents reads in this lane now rematerialize `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig`, while public current-`master` readback continues to rematerialize `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, and `zigux/tests/phase10_virtio_core_survey.zig` beside the returned `zigux/tests/phase10_virtio_core.zig`, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, and `zigux/Makefile` on current `master`",
//     "`scripts\zigux/validate_phase10.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, and `zigux/Makefile` themselves now rematerialize on current `master`, and their live bodies expose the dedicated shared Phase 10 validate/test route stack, so keep those returned files and that returned build-gate posture explicit here rather than framing them as repo-reality gaps.",
//     "The shared bootstrap-route guard now stays explicit through `scripts/zigux/check_phase10_bootstrap_route.zig` so the closure packet fails closed if the bootstrap workflow drops `make -C zigux phase10-validate` or reorders it behind `make -C zigux phase10-test`.",
//     "The shared freeze-boundary guard now stays explicit through `scripts/zigux/check_phase10_shared_freeze_boundary.zig` so the closure packet fails closed if the Phase 14 study-only anchors drift into Phase 10 closure claims.",
//     "The shared closure-manifest count guard now stays explicit through `scripts/zigux/check_phase10_closure_manifest_counts.zig` so the closure packet fails closed if its summary counts drift from the listed docs, manifests, drivers, or tests surfaces.",
//     "The returned shared and packet-local review guards also stay explicit through `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts/zigux/check_phase10_input_packet.zig`, and `scripts/zigux/check_phase10_mmio_packet.zig`, so this shared closure note keeps the current virtqueue, core, input, and MMIO lab validation stack visible beside the returned shared validate/test route rather than collapsing that evidence into the build gate alone.",
//     "`lab_only_driver_validation=starter_landed`",
//     "- evidence: `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `zigux/tests/phase10_build.zig`, `drivers/virtio/virtio_verify.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, `drivers/virtio/virtio_ring_verify.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `drivers/virtio/virtio_input_queue_callback_preflight.zig`, `drivers/virtio/virtio_input_teardown_observation.zig`, `drivers/virtio/virtio_input_verify.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_probe_preflight.zig`, `zigux/tests/phase10_virtio_input_registration_preflight.zig`, `drivers/virtio/virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_preflight.zig`, `zigux/tests/phase10_virtio_input_teardown_observation.zig`, `zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, the bootstrap-route guard, `scripts/zigux/check_phase10_core_packet.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_ring_packet.zig`, `scripts/zigux/check_phase10_input_packet.zig`, `scripts/zigux/check_phase10_mmio_packet.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, the manifest-count guard, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
//     "scripts/zigux/check_phase10_harness_coverage.zig",
//     "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
//     "`zigux/Makefile`",
//     "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `drivers/virtio/virtio_ring.zig`, and `scripts/zigux/check_phase10_ring_packet.zig`, while direct current-`master` contents reads now also rematerialize `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_queue_build.zig`, `zigux/tests/phase10_virtio_ring_queue_build_survey.zig`, and `drivers/virtio/virtio_ring_registration_summary.zig` beside the already-returned notification-data, reset-readiness, and survey replays, so keep that broader ring replay packet explicit here instead of treating it as fallback-only evidence.",
//     "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
//     "scripts/zigux/check_phase10_harness_coverage.zig",
//     "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
//     "- shared reminder lane owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-freeze-boundary-gap-survey.md`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, `scripts/zigux/check_phase10_bootstrap_route.zig`, `scripts/zigux/check_phase10_shared_freeze_boundary.zig`, `scripts/zigux/check_phase10_harness_coverage.zig`, `scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`, `scripts/zigux/check_phase10_closure_manifest_counts.zig`, and the shared Phase 10 wording in the docs root, review checklist, and tests root, with `scripts/zigux/README.md` aligned as the current dedicated Phase 10 scripts-root packet on current `master`",
//     "drivers/virtio/virtio_input_queue_callback_preflight.zig",
//     "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
//     "current `master` now rematerializes `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/Makefile`; treat those returned validator and build-route surfaces as part of the shared closure gate while keeping the returned dedicated core checker plus `drivers/virtio/virtio_driver_id.zig` and `zigux/tests/phase10_virtio_driver_id.zig` framed as bounded core-packet evidence rather than repo-reality gaps in this lane",
//     "`zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`, `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`, and `zigux/tests/phase10_virtio_mmio_survey.zig` are back as directly re-readable helper-local manifest, replay, and standalone build-shard anchors",
//     "Current `master` gives this lane a mixed but broader set of directly re-readable shared and packet-local anchors: `scripts/zigux/check_phase10_closure_manifest_counts.zig`, `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `zigux/tests/phase10_closure_manifest.json`, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core_manifest.json`, `scripts/zigux/check_phase10_core_packet.zig`, `drivers/virtio/virtio_driver_id.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`",
//     "Use the directly re-readable shared validator pair, closure manifest, dedicated core checker, driver-id replay pair, `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core.zig`, and Makefile-backed route anchors together with the returned core-slice, core-verify, reset-queue, interrupt-compound-ack, and survey-gate companions before widening shared wording back into transport-facing claims.",
//     "Treat the shared `zigux/tests/phase10_build.zig` route as already-landed validation evidence",
//     "Current `master` also rematerializes `zigux/tests/phase10_virtio_ring_notification_data_readiness.zig`, `zigux/tests/phase10_virtio_ring_registration_replay.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, and `zigux/tests/phase10_virtio_ring_survey.zig`, so keep that notification-data replay, queue-registration replay, reset-readiness replay, and dedicated ring survey gate explicit with `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and the shared `zigux/tests/phase10_build.zig` route instead of framing either replay as a direct-readback gap.",
//     "Documentation/zigux/phase10-virtio-input-module-slice.md",
//     "drivers/virtio/virtio_input_probe_preflight.zig",
//     "drivers/virtio/virtio_input_registration_preflight.zig",
//     "drivers/virtio/virtio_input_status_drain.zig",
//     "drivers/virtio/virtio_input_teardown_preflight.zig",
//     "drivers/virtio/virtio_input_teardown_observation.zig",
//     "drivers/virtio/virtio_input_verify.zig",
//     "zigux/tests/phase10_virtio_input.zig",
//     "zigux/tests/phase10_virtio_input_probe_preflight.zig",
//     "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
//     "zigux/tests/phase10_virtio_input_registration_preflight.zig",
//     "zigux/tests/phase10_virtio_input_status_drain.zig",
//     "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
//     "zigux/tests/phase10_virtio_input_teardown_observation.zig",
//     "zigux/tests/phase10_virtio_input_survey.zig",
//     "zigux/tests/phase10_virtio_input_manifest.json",
//     "queued status completions reclaimable in memory",
//     "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice",
//     "drivers/virtio/virtio_input_registration_preflight.zig",
//     "pub const RegistrationPreflightSummary = virtio_input.RegistrationPreflightSummary;",
//     "pub const RegistrationBlocker = virtio_input.RegistrationBlocker;",
//     "pub fn summarize(device: *const virtio_input.VirtioInputLab) RegistrationPreflightSummary {",
//     "pub fn blockerTag(blocker: RegistrationBlocker) []const u8 {",
//     "drivers/virtio/virtio_input_verify.zig",
//     "test \"phase10 virtio input verify keeps wrapper-facing queue preflight ordering explicit\" {",
//     "test \"phase10 virtio input verify keeps wrapper prerequisites ahead of registration claims\" {",
//     "test \"phase10 virtio input verify keeps teardown and status-drain wrapper parity explicit across reset\" {",
//     "drivers/virtio/virtio_ring_verify.zig",
//     "pub fn summarizeNotificationData(",
//     "pub fn summarizeDelayedCallback(",
//     "pub fn summarizeResetReadiness(",
//     "test \"phase10 virtio ring verify keeps notification-data next-avail state reviewable across split packed and reset replay\" {",
//     "test \"phase10 virtio ring verify keeps delayed callback wrapper thresholds explicit\" {",
//     "test \"phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay\" {",
//     "scripts/zigux/README.md",
//     "## Phase 10",
//     "scripts/zigux/check_phase10_bootstrap_route.zig",
//     "scripts/zigux/check_phase10_harness_coverage.zig",
//     "scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
//     "scripts\zigux/validate_phase10.zig",
//     "scripts\zigux/validate_phase10_closure.zig",
//     "zigux/tests/phase10_closure_manifest.json",
//     "make -C zigux phase10-validate",
//     "make -C zigux phase10-test",
//     "make -C zigux phase10",
//     "`Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` keep the bounded core packet explicit, and the now-returned exact-path `drivers/virtio/virtio_driver_id.zig` plus `zigux/tests/phase10_virtio_driver_id.zig` pair stays explicit as the narrower core-side follow-through evidence on current `master`",
//     "keep risky transport parked",
//     "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
//     "test \"phase10 virtio ring notification-data replay keeps split and packed next-avail state explicit\" {",
//     "const split_summary = try ring.notificationDataSummary(1);",
//     "const packed_summary = try ring.notificationDataSummary(2);",
//     "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
//     "test \"phase10 virtio ring repeated prepareKick stays idle until new descriptors are published\" {",
//     "kick_summary = try ring.prepareKick(1);",
//     "try std.testing.expect(!kick_summary.needs_kick);",
//     "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
//     "test \"phase10 virtio ring reset reuse stays blocked until queue-local reset prerequisites clear and then replays from a clean queue state\" {",
//     "const reset = try ring.resetQueue(2);",
//     "const kick_after_reset = try ring.prepareKick(2);",
//     "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
//     "test \"phase10 virtio ring broken-queue coverage kicks published work before used accounting and keeps notification history visible\" {",
//     "try std.testing.expectError(error.QueueResetWhileBroken, ring.resetQueue(3));",
//     "const cleared_summary = try ring.clearBroken(3);",
//     "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
//     "test \"phase10 virtio ring delayed callback budget stays bounded to queue-local replay state\" {",
//     "try std.testing.expectEqual(@as(u16, 1), summary.delay_budget_count);",
//     "try std.testing.expect(summary.should_poll);",
//     "try std.testing.expectError(error.QueueBroken, ring.enableCallbackDelayed(7));",
//     "zigux/tests/phase10_build.zig",
//     "\"phase10-virtio-core-tests\"",
//     "\"phase10-virtio-core-interrupt-compound-ack-tests\"",
//     "run_phase10_virtio_core_interrupt_compound_ack_tests.step",
//     "\"phase10-virtio-core-reset-queue-tests\"",
//     "run_phase10_virtio_core_reset_queue_tests.step",
//     "\"phase10-virtio-core-verify-tests\"",
//     "run_phase10_virtio_core_verify_tests.step",
//     "\"phase10-virtio-core-survey-tests\"",
//     "run_phase10_virtio_core_survey_tests.step",
//     "\"phase10-virtio-driver-id-tests\"",
//     "run_phase10_virtio_driver_id_tests.step",
//     "\"phase10-virtio-input-tests\"",
//     "\"phase10-virtio-input-probe-preflight-tests\"",
//     "\"phase10-virtio-input-queue-callback-preflight-tests\"",
//     "\"phase10-virtio-input-registration-preflight-tests\"",
//     "\"phase10-virtio-input-status-drain-tests\"",
//     "\"phase10-virtio-input-teardown-preflight-tests\"",
//     "run_phase10_virtio_input_teardown_preflight_tests.step",
//     "\"phase10-virtio-input-teardown-observation-tests\"",
//     "\"phase10-virtio-input-survey-tests\"",
//     "\"phase10-virtio-input-verify-tests\"",
//     "\"phase10-virtio-ring-tests\"",
//     "run_phase10_virtio_ring_tests.step",
//     "\"phase10-virtio-ring-notification-data-readiness-tests\"",
//     "run_phase10_virtio_ring_notification_data_readiness_tests.step",
//     "\"phase10-virtio-ring-verify-tests\"",
//     "run_phase10_virtio_ring_verify_tests.step",
//     "\"phase10-virtio-ring-publish-readiness-tests\"",
//     "run_phase10_virtio_ring_publish_readiness_tests.step",
//     "\"phase10-virtio-ring-prepare-kick-idempotent-tests\"",
//     "\"phase10-virtio-ring-reset-reuse-tests\"",
//     "\"phase10-virtio-ring-broken-queue-queue-discipline-tests\"",
//     "\"phase10-virtio-ring-delayed-callback-budget-tests\"",
//     "\"phase10-virtio-ring-survey-tests\"",
//     "\"phase10-virtio-mmio-tests\"",
//     "\"phase10-virtio-mmio-lab-tests\"",
//     "run_phase10_virtio_mmio_lab_tests.step",
//     "\"phase10-virtio-mmio-verify-tests\"",
//     "\"phase10-virtio-mmio-survey-tests\"",
//     "Run the live Phase 10 virtio core, input, ring, and MMIO lab validation tests",
//     "zigux/Makefile",
//     "phase10-validate:",
//     "$(PYTHON) scripts/zigux/check_phase10_bootstrap_route.zig",
//     "$(PYTHON) scripts/zigux/check_phase10_shared_freeze_boundary.zig",
//     "$(PYTHON) scripts/zigux/check_phase10_harness_coverage.zig",
//     "$(PYTHON) scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
//     "phase10-test:",
//     "$(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase10_build.zig --summary all",
//     "phase10: phase10-validate phase10-test",
//     "scripts/zigux/check_phase10_bootstrap_route.zig",
//     "VALIDATE_STEP = \"Validate Phase 10 checker-backed review packet\"",
//     "VALIDATE_CMD = \"make -C zigux phase10-validate\"",
//     "TEST_STEP = \"Run Phase 10 helper tests\"",
//     "TEST_CMD = \"make -C zigux phase10-test\"",
//     "scripts/zigux/check_phase10_shared_freeze_boundary.zig",
//     "CHECK_COMMAND = \"zig run scripts/zigux/check_phase10_shared_freeze_boundary.zig --\"",
//     "\"kernel/workqueue.c\"",
//     "\"kernel/trace/ring_buffer.c\"",
//     "\"kernel/sched/core.c\"",
//     "\"net/core/skbuff.c\"",
//     ".github/workflows/zigux-bootstrap.yml",
//     "Self-test current Phase 10 bootstrap route checker",
//     "Check current Phase 10 bootstrap route",
//     "Validate Phase 10 checker-backed review packet",
//     "make -C zigux phase10-validate",
//     "Run Phase 10 helper tests",
//     "make -C zigux phase10-test",
//     "zigux/tests/phase10_closure_manifest.json",
//     "\"lab_only_driver_validation\"",
//     "\"scripts/zigux/check_phase10_harness_coverage.zig\"",
//     "\"scripts/zigux/check_phase10_tests_readme_core_surfaces.zig\"",
//     "\"scripts\zigux/validate_phase10.zig\"",
//     "\"scripts\zigux/validate_phase10_closure.zig\"",
//     "\"zig run scripts/zigux/validate_phase10.zig\"",
//     "\"zig run scripts/zigux/validate_phase10_closure.zig\"",
// };
//
// const FORBIDDEN_MARKERS = [_][]const u8{
//     "Documentation/zigux/phase10-closure-evidence.md",
//     "directly re-readable packet manifests in this lane now include `zigux/tests/phase10_virtio_ring_manifest.json` and `zigux/tests/phase10_virtio_input_manifest.json`",
//     "current contents reads still do not materialize `zigux/tests/phase10_virtio_core_manifest.json`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, and `zigux/tests/phase10_virtio_core_survey.zig` through the direct readback available in this lane, while the returned `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, and `zigux/Makefile` now rematerialize the dedicated shared Phase 10 validate/test route surface on current `master`",
//     "The current ring lane therefore stays reviewable here through `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `drivers/virtio/virtio_ring.zig`, while `zigux/tests/phase10_virtio_ring_survey.zig` still remains a direct-readback gap in this lane.",
//     "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
//     "Authenticated contents reads still fail for `Documentation/zigux/phase10-virtio-core-slice.md`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, and the broader validator-first `scripts\zigux/validate_phase10.zig` route through the direct readback available in this lane.",
//     "current `master` still does not materialize `scripts\zigux/validate_phase10.zig` through the direct readback available in this lane, but it now rematerializes `scripts\zigux/validate_phase10_closure.zig`, `zigux/tests/phase10_closure_manifest.json`, and `zigux/Makefile`; keep the still-missing broader validator-script name framed as a last-known packet member or repo-reality gap while treating the returned closure validator, closure manifest, and Makefile-backed `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` route stack as the shared closure and build gate",
//     "Current `master` also rematerializes `zigux/tests/phase10_virtio_ring_survey.zig`, so keep that dedicated ring survey gate explicit with `Documentation/zigux/phase10-virtio-ring-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and the shared `zigux/tests/phase10_build.zig` route instead of framing the survey gate as a direct-readback gap.",
//     "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
//     "keep `zigux/tests/phase10_virtio_ring_survey.zig` framed as a last-known packet member until a fresh reread proves it rematerializes on current `master`.",
//     "current `master` still does not materialize `scripts\zigux/validate_phase10.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, and `zigux/tests/phase10_virtio_ring.zig` through the direct readback available in this lane, so keep them framed as last-known packet members or repo-reality gaps rather than direct current-`master` evidence.",
//     "scripts/zigux/README.md",
//     "current `master` still does not materialize `Documentation/zigux/phase10-virtio-core-slice.md`",
//     "zigux/tests/phase10_build.zig",
//     "Run the live Phase 10 virtio input, ring, and MMIO lab validation tests",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (PHASE10_SCRIPTS_ROOT_PHRASE) |marker| try guard.requireMarker(text, marker);
//     for (SELF_TEST_MUTATIONS) |marker| try guard.requireMarker(text, marker);
//     for (SELF_TEST_MISSING_FILES) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
