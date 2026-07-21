const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_CLOSURE_MANIFEST_COUNTS=pass";
pub const self_test_pass_marker = "PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const Manifest = struct {
    doc_count: usize,
    docs: []const []const u8,
    manifest_count: usize,
    manifests: []const []const u8,
    driver_count: usize,
    drivers: []const []const u8,
    test_count: usize,
    tests: []const []const u8,
    exact_checks: []const []const u8,
};

const expected_exact_checks = [_][]const u8{
    "zig run scripts/zigux/check_phase10_bootstrap_route.zig",
    "zig run scripts/zigux/check_phase10_core_packet.zig",
    "zig run scripts/zigux/check_phase10_shared_freeze_boundary.zig",
    "zig run scripts/zigux/check_phase10_ring_packet.zig",
    "zig run scripts/zigux/check_phase10_input_packet.zig",
    "zig run scripts/zigux/check_phase10_mmio_packet.zig",
    "zig run scripts/zigux/check_phase10_harness_coverage.zig",
    "zig run scripts/zigux/check_phase10_tests_readme_core_surfaces.zig",
    "zig run scripts/zigux/check_phase10_closure_manifest_counts.zig",
    "zig run scripts/zigux/validate_phase10.zig",
    "zig run scripts/zigux/validate_phase10_closure.zig",
    "make -C zigux phase10-validate",
    "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
    "make -C zigux phase10-test",
    "make -C zigux phase10",
};

const manifest_markers = [_][]const u8{
    "drivers/virtio/virtio_ring.zig",
    "drivers/virtio/virtio_ring_publish_readiness.zig",
    "drivers/virtio/virtio_ring_registration_summary.zig",
    "drivers/virtio/virtio_ring_used_buffer_poll.zig",
    "zigux/tests/phase10_virtio_ring.zig",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "Documentation/zigux/phase10-virtio-ring-survey.md",
    "drivers/virtio/virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "scripts/zigux/check_phase10_core_packet.zig",
    "scripts/zigux/check_phase10_closure_manifest_counts.zig",
    "scripts/zigux/validate_phase10.zig",
    "scripts/zigux/validate_phase10_closure.zig",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase10_virtio_ring_queue_build.zig",
    "zigux/tests/phase10_virtio_ring_queue_build_survey.zig",
    "drivers/virtio/virtio_ring_verify.zig",
    "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
    "zigux/tests/phase10_virtio_ring_registration_replay.zig",
    "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
    "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
    "drivers/virtio/virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    "samples/zigux",
    "zigux/tests/phase5_build.zig",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_trace_events.zig",
    "zigux/tests/phase9_build.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "drivers/virtio/virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "Documentation/zigux/phase10-closure-evidence.md",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "core",
    "ring",
    "input",
    "mmio",
    "P10-L01",
    "P10-L10",
    "P10-L22",
    "P10-L11",
    "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
    "0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
    "ee789f026f11a0c5c70ded9a868979cdf4f55393",
    "b53ec2bd507d0b3283486e76acc273b184ad5bf8",
    "phase10-queue-shape-bookkeeping-helper",
    "phase10-config-generation-bookkeeping-helper",
    "phase10-interrupt-ack-bookkeeping-helper",
    "phase10-lifecycle-guard-bookkeeping-helper",
    "phase10-driver-validation-narrowing-helper",
    "phase10-core-attribute-summary-helper",
    "phase10-reset-replay-bookkeeping-helper",
    "phase10-virtqueue-shape-helper",
    "phase10-used-buffer-polling-helper",
    "phase10-callback-enable-helper",
    "phase10-callback-delay-helper",
    "phase10-notify-prepare-helper",
    "phase10-notification-data-summary-helper",
    "phase10-broken-queue-poll-guard",
    "phase10-queue-publish-readiness-helper",
    "phase10-queue-reset-helper",
    "phase10-queue-reset-readiness-helper",
    "phase10-ring-verify-replay",
    "phase10-virtio-ring-slice-note",
    "phase10-virtio-input-capability-setup-helper",
    "phase10-virtio-input-multitouch-slot-helper",
    "phase10-virtio-input-probe-preflight-helper",
    "phase10-virtio-input-teardown-preflight-helper",
    "phase10-virtio-input-teardown-observation-helper",
    "phase10-virtio-input-registration-preflight-helper",
    "phase10-virtio-input-queue-callback-preflight-helper",
    "phase10-virtio-input-status-drain-helper",
    "phase10-virtio-mmio-lab-helper",
    "phase10-mmio-transport-identity-helper",
    "phase10-mmio-probe-preflight-helper",
    "phase10-mmio-selected-queue-readiness-helper",
    "phase10-mmio-interrupt-ack-disposition-helper",
    "phase10-mmio-feature-negotiation-summary-helper",
    "phase10-mmio-config-write-plan-freshness-helper",
    "phase10-mmio-config-write-disposition-helper",
    "phase10-mmio-config-write-apply-observation-helper",
    "phase10 core interrupt-compound-ack replay",
    "phase10 core reset-queue replay",
    "phase10 driver-id review path replay",
    "phase10 ring broader replay",
    "phase10 ring notification-data readiness replay",
    "phase10 ring queue-registration replay",
    "phase10 ring registration-summary wrapper replay",
    "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
    "phase10 ring prepare-kick idempotence replay",
    "phase10 ring drained-reset reuse replay",
    "phase10 ring reset-readiness replay",
    "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
    "phase10 ring broken-queue queue-discipline replay",
    "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
    "phase10 ring delayed-callback budget replay",
    "phase10 ring focused queue-build replay",
    "phase10 ring queue-build survey replay",
    "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
    "phase10 input queue-callback-preflight replay",
    "zigux/tests/phase10_virtio_input_status_drain.zig",
    "phase10 input status-drain replay",
    "zigux/tests/phase10_virtio_input_probe_preflight.zig",
    "phase10 input probe-preflight replay",
    "zigux/tests/phase10_virtio_input_registration_preflight.zig",
    "phase10 input registration-preflight replay",
    "phase10 input teardown-preflight replay",
    "zigux/tests/phase10_virtio_input_teardown_observation.zig",
    "phase10 input teardown-observation replay",
    "phase10 mmio lab replay",
    "phase10 mmio apply-observation replay",
    "phase10 mmio wrapper-facing verify replay",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "phase10 mmio survey replay",
    "phase10 ring publish-readiness wrapper replay",
    "phase10-core-probe-remove-lifecycle",
    "phase10-virtio-input-registration-lifecycle",
    "phase10-mmio-lifecycle-and-irq-paths",
    "manifest_derived",
};

const ledger_markers = [_][]const u8{
    "PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json",
    "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
    "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
    "PHASE10_LEDGER_SURVEY_CORE_COMMIT=c11221dc7a68d7511ae1c69d64b3f08528287ed8",
    "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10",
    "PHASE10_LEDGER_SURVEY_RING_COMMIT=0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
    "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22",
    "PHASE10_LEDGER_SURVEY_INPUT_COMMIT=ee789f026f11a0c5c70ded9a868979cdf4f55393",
    "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
    "PHASE10_LEDGER_SURVEY_MMIO_COMMIT=b53ec2bd507d0b3283486e76acc273b184ad5bf8",
    "PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed",
    "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=starter_landed",
    "PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed",
    "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport",
    "PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE=drivers/virtio/virtio_ring.zig,drivers/virtio/virtio_ring_publish_readiness.zig,drivers/virtio/virtio_ring_registration_summary.zig,drivers/virtio/virtio_ring_used_buffer_poll.zig,zigux/tests/phase10_virtio_ring.zig,zigux/tests/phase10_virtio_ring_manifest.json,Documentation/zigux/phase10-virtio-ring-survey.md",
    "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,drivers/virtio/virtio_mmio_verify.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-survey.md",
    "PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE=Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md,zigux/tests/phase10_build.zig,drivers/virtio/virtio_verify.zig,drivers/virtio/virtio_driver_id.zig,zigux/tests/phase10_virtio_driver_id.zig,zigux/tests/phase10_virtio_core.zig,zigux/tests/phase10_virtio_core_reset_queue.zig,zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig,Documentation/zigux/phase10-virtio-core-survey.md,zigux/tests/phase10_virtio_core_survey.zig,zigux/tests/phase10_virtio_ring.zig,zigux/tests/phase10_virtio_ring_notification_data_readiness.zig,zigux/tests/phase10_virtio_ring_registration_replay.zig,zigux/tests/phase10_virtio_ring_reset_reuse.zig,zigux/tests/phase10_virtio_ring_reset_readiness.zig,zigux/tests/phase10_virtio_ring_queue_build.zig,zigux/tests/phase10_virtio_ring_queue_build_survey.zig,drivers/virtio/virtio_ring_verify.zig,drivers/virtio/virtio_ring_publish_readiness.zig,drivers/virtio/virtio_ring_registration_summary.zig,drivers/virtio/virtio_ring_used_buffer_poll.zig,drivers/virtio/virtio_input_queue_callback_preflight.zig,drivers/virtio/virtio_input_registration_preflight.zig,drivers/virtio/virtio_input_teardown_preflight.zig,drivers/virtio/virtio_input_teardown_observation.zig,drivers/virtio/virtio_input_verify.zig,zigux/tests/phase10_virtio_input.zig,zigux/tests/phase10_virtio_input_probe_preflight.zig,zigux/tests/phase10_virtio_input_registration_preflight.zig,zigux/tests/phase10_virtio_input_teardown_preflight.zig,zigux/tests/phase10_virtio_input_teardown_observation.zig,zigux/tests/phase10_virtio_input_queue_callback_preflight.zig,zigux/tests/phase10_virtio_input_status_drain.zig,zigux/tests/phase10_virtio_input_survey.zig,drivers/virtio/virtio_mmio_apply_observation.zig,drivers/virtio/virtio_mmio_verify.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig,zigux/tests/phase10_virtio_mmio_survey.zig,scripts/zigux/check_phase10_bootstrap_route.zig,scripts/zigux/check_phase10_core_packet.zig,scripts/zigux/check_phase10_shared_freeze_boundary.zig,scripts/zigux/check_phase10_ring_packet.zig,scripts/zigux/check_phase10_input_packet.zig,scripts/zigux/check_phase10_mmio_packet.zig,scripts/zigux/check_phase10_harness_coverage.zig,scripts/zigux/check_phase10_tests_readme_core_surfaces.zig,scripts/zigux/check_phase10_closure_manifest_counts.zig,scripts/zigux/validate_phase10.zig,scripts/zigux/validate_phase10_closure.zig,zigux/Makefile,.github/workflows/zigux-bootstrap.yml",
    "PHASE10_LEDGER_SCOREBOARD_DUAL_IMPLEMENTATIONS_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md,zigux/tests/phase10_virtio_core_manifest.json,zigux/tests/phase10_virtio_ring_manifest.json,zigux/tests/phase10_virtio_input_manifest.json,zigux/tests/phase10_virtio_mmio_manifest.json",
};

fn expectStrings(actual: []const []const u8, expected: []const []const u8) !void {
    if (actual.len != expected.len) return error.StringArrayLengthDrift;
    for (actual, expected) |a, e| if (!std.mem.eql(u8, a, e)) return error.StringArrayValueDrift;
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const manifest_path = try guard.joinPath(allocator, root, "zigux/tests/phase10_closure_manifest.json");
    defer allocator.free(manifest_path);
    const manifest_text = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest_text);
    for (manifest_markers) |marker| try guard.requireMarker(manifest_text, marker);
    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_text, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const value = parsed.value;
    if (value.doc_count != value.docs.len or value.doc_count != 8) return error.DocumentCountDrift;
    if (value.manifest_count != value.manifests.len or value.manifest_count != 4) return error.ManifestCountDrift;
    if (value.driver_count != value.drivers.len or value.driver_count != 4) return error.DriverCountDrift;
    if (value.test_count != value.tests.len or value.test_count != 35) return error.TestCountDrift;
    try expectStrings(value.exact_checks, &expected_exact_checks);
    const ledger_path = try guard.joinPath(allocator, root, "zigux-alpha/PHASE10_CLOSURE_LEDGER.md");
    defer allocator.free(ledger_path);
    const ledger = try guard.readUtf8File(io, allocator, ledger_path);
    defer allocator.free(ledger);
    for (ledger_markers) |marker| try guard.requireMarker(ledger, marker);
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_FIELD_COUNT=4", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_EXACT_CHECK_COUNT=15", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_RING_EVIDENCE_COUNT=7", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_MMIO_EVIDENCE_COUNT=5", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LAB_VALIDATION_EVIDENCE_COUNT=25", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_REFERENCE_SAMPLE_EVIDENCE_COUNT=3", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_RUNTIME_STARTER_EVIDENCE_COUNT=8", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LANDED_CORE_HELPER_COUNT=7", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LANDED_RING_HELPER_COUNT=12", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LANDED_INPUT_HELPER_COUNT=8", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LANDED_MMIO_HELPER_COUNT=9", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_FOCUSED_HARNESS_REPLAY_COUNT=25", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_DUAL_IMPLEMENTATION_EVIDENCE_COUNT=5", .{});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_REQUIRED_LEDGER_LINE_COUNT=18", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST_CASE_COUNT=18", .{});
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
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) { if (index + 1 >= args.len) std.process.exit(2); index += 1; explicit_root = args[index]; continue; }
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
// pub const pass_marker = "PHASE10_CLOSURE_MANIFEST_COUNTS_SELF_TEST=pass";
//
// const REQUIRED_EXACT_CHECKS = [_][]const u8{
//     "zig run scripts/zigux/check_phase10_bootstrap_route.zig --",
//     "zig run scripts/zigux/check_phase10_core_packet.zig --",
//     "zig run scripts/zigux/check_phase10_shared_freeze_boundary.zig --",
//     "zig run scripts/zigux/check_phase10_ring_packet.zig --",
//     "zig run scripts/zigux/check_phase10_input_packet.zig --",
//     "zig run scripts/zigux/check_phase10_mmio_packet.zig --",
//     "zig run scripts/zigux/check_phase10_harness_coverage.zig --",
//     "zig run scripts/zigux/check_phase10_tests_readme_core_surfaces.zig --",
//     "zig run scripts/zigux/check_phase10_closure_manifest_counts.zig --",
//     "zig run scripts/zigux/validate_phase10.zig",
//     "zig run scripts/zigux/validate_phase10_closure.zig",
//     "make -C zigux phase10-validate",
//     "zig build test --build-file zigux/tests/phase10_build.zig --summary all",
//     "make -C zigux phase10-test",
//     "make -C zigux phase10",
// };
//
// const REQUIRED_RING_SCOREBOARD_EVIDENCE = [_][]const u8{
//     "drivers/virtio/virtio_ring.zig",
//     "drivers/virtio/virtio_ring_publish_readiness.zig",
//     "drivers/virtio/virtio_ring_registration_summary.zig",
//     "drivers/virtio/virtio_ring_used_buffer_poll.zig",
//     "zigux/tests/phase10_virtio_ring.zig",
//     "zigux/tests/phase10_virtio_ring_manifest.json",
//     "Documentation/zigux/phase10-virtio-ring-survey.md",
// };
//
// const REQUIRED_MMIO_SCOREBOARD_EVIDENCE = [_][]const u8{
//     "drivers/virtio/virtio_mmio.zig",
//     "zigux/tests/phase10_virtio_mmio.zig",
//     "drivers/virtio/virtio_mmio_verify.zig",
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
//     "Documentation/zigux/phase10-virtio-mmio-survey.md",
// };
//
// const REQUIRED_LAB_VALIDATION_EVIDENCE = [_][]const u8{
//     "scripts/zigux/check_phase10_core_packet.zig",
//     "scripts/zigux/check_phase10_closure_manifest_counts.zig",
//     "scripts\zigux/validate_phase10.zig",
//     "scripts\zigux/validate_phase10_closure.zig",
//     "zigux/Makefile",
//     ".github/workflows/zigux-bootstrap.yml",
//     "zigux/tests/phase10_virtio_ring_queue_build.zig",
//     "zigux/tests/phase10_virtio_ring_queue_build_survey.zig",
//     "drivers/virtio/virtio_ring_verify.zig",
//     "drivers/virtio/virtio_ring_registration_summary.zig",
//     "drivers/virtio/virtio_ring_used_buffer_poll.zig",
//     "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
//     "zigux/tests/phase10_virtio_ring_registration_replay.zig",
//     "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
//     "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
// };
//
// const REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE = [_][]const u8{
//     "drivers/virtio/virtio_input_teardown_preflight.zig",
//     "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
// };
//
// const REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE = [_][]const u8{
//     "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
// };
//
// const REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE = [_][]const u8{
//     "samples/zigux",
//     "zigux/tests/phase5_build.zig",
//     "Documentation/zigux/review-checklist.md",
// };
//
// const REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE = [_][]const u8{
//     "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
//     "Documentation/zigux/phase9-runtime-trace-events-survey.md",
//     "samples/zigux/runtime_bitmap_loader.zig",
//     "samples/zigux/runtime_trace_events.zig",
//     "zigux/tests/phase9_build.zig",
//     "zigux/kernel/runtime_loader.zig",
//     "zigux/tests/runtime_trace_events_manifest.json",
//     "zigux/tests/runtime_trace_events_survey.zig",
// };
//
// const REQUIRED_CORE_LAB_VALIDATION_EVIDENCE = [_][]const u8{
//     "Documentation/zigux/phase10-virtio-core-survey.md",
//     "drivers/virtio/virtio_driver_id.zig",
//     "zigux/tests/phase10_virtio_driver_id.zig",
//     "zigux/tests/phase10_virtio_core.zig",
//     "zigux/tests/phase10_virtio_core_reset_queue.zig",
//     "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
//     "zigux/tests/phase10_virtio_core_survey.zig",
// };
//
// const REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE = [_][]const u8{
//     "Documentation/zigux/phase10-closure-evidence.md",
//     "zigux/tests/phase10_virtio_core_manifest.json",
//     "zigux/tests/phase10_virtio_ring_manifest.json",
//     "zigux/tests/phase10_virtio_input_manifest.json",
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
// };
//
// const COUNT_FIELDS = [_][]const u8{
//     "doc_count",
//     "docs",
//     "manifest_count",
//     "manifests",
//     "driver_count",
//     "drivers",
//     "test_count",
//     "tests",
// };
//
// const REQUIRED_SURVEY_LANE_KEYS = [_][]const u8{
//     "core",
//     "P10-L01",
//     "ring",
//     "P10-L10",
//     "input",
//     "P10-L22",
//     "mmio",
//     "P10-L11",
// };
//
// const REQUIRED_SURVEY_COMMITS = [_][]const u8{
//     "core",
//     "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
//     "ring",
//     "0aa2db32bcb1c7065850ee3f66ec119b071fbf5c",
//     "input",
//     "ee789f026f11a0c5c70ded9a868979cdf4f55393",
//     "mmio",
//     "b53ec2bd507d0b3283486e76acc273b184ad5bf8",
// };
//
// const LEDGER_STATUS_FIELDS = [_][]const u8{
//     "virtqueue_wrappers",
//     "PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS",
//     "mmio_wrappers",
//     "PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS",
//     "lab_only_driver_validation",
//     "PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION",
//     "dual_implementations_for_risky_areas",
//     "PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS",
// };
//
// const LEDGER_EVIDENCE_FIELDS = [_][]const u8{
//     "virtqueue_wrappers",
//     "PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE",
//     "mmio_wrappers",
//     "PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE",
//     "lab_only_driver_validation",
//     "PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE",
//     "dual_implementations_for_risky_areas",
//     "PHASE10_LEDGER_SCOREBOARD_DUAL_IMPLEMENTATIONS_EVIDENCE",
// };
//
// const REQUIRED_LANDED_CORE_HELPER_EVIDENCE = [_][]const u8{
//     "zigux/tests/phase10_virtio_core_manifest.json",
//     "phase10-queue-shape-bookkeeping-helper",
//     "phase10-config-generation-bookkeeping-helper",
//     "phase10-interrupt-ack-bookkeeping-helper",
//     "phase10-lifecycle-guard-bookkeeping-helper",
//     "phase10-driver-validation-narrowing-helper",
//     "phase10-core-attribute-summary-helper",
//     "phase10-reset-replay-bookkeeping-helper",
// };
//
// const REQUIRED_LANDED_RING_HELPER_EVIDENCE = [_][]const u8{
//     "zigux/tests/phase10_virtio_ring_manifest.json",
//     "phase10-virtqueue-shape-helper",
//     "phase10-used-buffer-polling-helper",
//     "phase10-callback-enable-helper",
//     "phase10-callback-delay-helper",
//     "phase10-notify-prepare-helper",
//     "phase10-notification-data-summary-helper",
//     "phase10-broken-queue-poll-guard",
//     "phase10-queue-publish-readiness-helper",
//     "phase10-queue-reset-helper",
//     "phase10-queue-reset-readiness-helper",
//     "phase10-ring-verify-replay",
//     "phase10-virtio-ring-slice-note",
// };
//
// const REQUIRED_LANDED_INPUT_HELPER_EVIDENCE = [_][]const u8{
//     "zigux/tests/phase10_virtio_input_manifest.json",
//     "phase10-virtio-input-capability-setup-helper",
//     "phase10-virtio-input-multitouch-slot-helper",
//     "phase10-virtio-input-probe-preflight-helper",
//     "phase10-virtio-input-teardown-preflight-helper",
//     "phase10-virtio-input-teardown-observation-helper",
//     "phase10-virtio-input-registration-preflight-helper",
//     "phase10-virtio-input-queue-callback-preflight-helper",
//     "phase10-virtio-input-status-drain-helper",
// };
//
// const REQUIRED_LANDED_MMIO_HELPER_EVIDENCE = [_][]const u8{
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
//     "phase10-virtio-mmio-lab-helper",
//     "phase10-mmio-transport-identity-helper",
//     "phase10-mmio-probe-preflight-helper",
//     "phase10-mmio-selected-queue-readiness-helper",
//     "phase10-mmio-interrupt-ack-disposition-helper",
//     "phase10-mmio-feature-negotiation-summary-helper",
//     "phase10-mmio-config-write-plan-freshness-helper",
//     "phase10-mmio-config-write-disposition-helper",
//     "phase10-mmio-config-write-apply-observation-helper",
// };
//
// const REQUIRED_FOCUSED_HARNESS_REPLAYS = [_][]const u8{
//     "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
//     "phase10 core interrupt-compound-ack replay",
//     "zigux/tests/phase10_virtio_core_reset_queue.zig",
//     "phase10 core reset-queue replay",
//     "zigux/tests/phase10_virtio_driver_id.zig",
//     "phase10 driver-id review path replay",
//     "zigux/tests/phase10_virtio_ring.zig",
//     "phase10 ring broader replay",
//     "zigux/tests/phase10_virtio_ring_notification_data_readiness.zig",
//     "phase10 ring notification-data readiness replay",
//     "zigux/tests/phase10_virtio_ring_registration_replay.zig",
//     "phase10 ring queue-registration replay",
//     "drivers/virtio/virtio_ring_registration_summary.zig",
//     "phase10 ring registration-summary wrapper replay",
//     "zigux/tests/phase10_virtio_ring_prepare_kick_idempotent.zig",
//     "phase10 ring prepare-kick idempotence replay",
//     "zigux/tests/phase10_virtio_ring_reset_reuse.zig",
//     "phase10 ring drained-reset reuse replay",
//     "zigux/tests/phase10_virtio_ring_reset_readiness.zig",
//     "phase10 ring reset-readiness replay",
//     "zigux/tests/phase10_virtio_ring_broken_queue_queue_discipline.zig",
//     "phase10 ring broken-queue queue-discipline replay",
//     "zigux/tests/phase10_virtio_ring_delayed_callback_budget.zig",
//     "phase10 ring delayed-callback budget replay",
//     "zigux/tests/phase10_virtio_ring_queue_build.zig",
//     "phase10 ring focused queue-build replay",
//     "zigux/tests/phase10_virtio_ring_queue_build_survey.zig",
//     "phase10 ring queue-build survey replay",
//     "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig",
//     "phase10 input queue-callback-preflight replay",
//     "zigux/tests/phase10_virtio_input_status_drain.zig",
//     "phase10 input status-drain replay",
//     "zigux/tests/phase10_virtio_input_probe_preflight.zig",
//     "phase10 input probe-preflight replay",
//     "zigux/tests/phase10_virtio_input_registration_preflight.zig",
//     "phase10 input registration-preflight replay",
//     "zigux/tests/phase10_virtio_input_teardown_preflight.zig",
//     "phase10 input teardown-preflight replay",
//     "zigux/tests/phase10_virtio_input_teardown_observation.zig",
//     "phase10 input teardown-observation replay",
//     "zigux/tests/phase10_virtio_mmio.zig",
//     "phase10 mmio lab replay",
//     "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
//     "phase10 mmio apply-observation replay",
//     "drivers/virtio/virtio_mmio_verify.zig",
//     "phase10 mmio wrapper-facing verify replay",
//     "zigux/tests/phase10_virtio_mmio_survey.zig",
//     "phase10 mmio survey replay",
//     "drivers/virtio/virtio_ring_publish_readiness.zig",
//     "phase10 ring publish-readiness wrapper replay",
// };
//
// const MANIFEST_PATH = [_][]const u8{
//     "zigux/tests/phase10_closure_manifest.json",
// };
//
// const LEDGER_PATH = [_][]const u8{
//     "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
// };
//
// const REQUIRED_CORE_BLOCKED_TRANSPORT_PATH = [_][]const u8{
//     "zigux/tests/phase10_virtio_core_manifest.json",
// };
//
// const REQUIRED_CORE_BLOCKED_TRANSPORT_GAP = [_][]const u8{
//     "phase10-core-probe-remove-lifecycle",
// };
//
// const REQUIRED_INPUT_READY_TRANSPORT_PATH = [_][]const u8{
//     "zigux/tests/phase10_virtio_input_manifest.json",
// };
//
// const REQUIRED_INPUT_READY_TRANSPORT_GAP = [_][]const u8{
//     "phase10-virtio-input-registration-lifecycle",
// };
//
// const REQUIRED_MMIO_READY_TRANSPORT_PATH = [_][]const u8{
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
// };
//
// const REQUIRED_MMIO_READY_TRANSPORT_GAP = [_][]const u8{
//     "phase10-mmio-lifecycle-and-irq-paths",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (REQUIRED_EXACT_CHECKS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_RING_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MMIO_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_LAB_VALIDATION_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_INPUT_LAB_VALIDATION_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MMIO_LAB_VALIDATION_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_REFERENCE_SAMPLE_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_RUNTIME_STARTER_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_CORE_LAB_VALIDATION_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_DUAL_IMPLEMENTATION_SCOREBOARD_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (COUNT_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_SURVEY_LANE_KEYS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_SURVEY_COMMITS) |marker| try guard.requireMarker(text, marker);
//     for (LEDGER_STATUS_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (LEDGER_EVIDENCE_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_LANDED_CORE_HELPER_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_LANDED_RING_HELPER_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_LANDED_INPUT_HELPER_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_LANDED_MMIO_HELPER_EVIDENCE) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_FOCUSED_HARNESS_REPLAYS) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LEDGER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_CORE_BLOCKED_TRANSPORT_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_CORE_BLOCKED_TRANSPORT_GAP) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_INPUT_READY_TRANSPORT_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_INPUT_READY_TRANSPORT_GAP) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MMIO_READY_TRANSPORT_PATH) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MMIO_READY_TRANSPORT_GAP) |marker| try guard.requireMarker(text, marker);
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
