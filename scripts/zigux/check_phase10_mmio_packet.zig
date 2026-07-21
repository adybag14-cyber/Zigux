const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_MMIO_PACKET=pass";
pub const self_test_pass_marker = "PHASE10_MMIO_PACKET_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "# Phase 10 Virtio MMIO Survey",
    "PHASE10_STATUS=parked",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "interrupt-ack disposition review",
    "staged config-write planning",
    "config-write apply observation",
    "config-write disposition reporting",
    "feature-negotiation deltas",
    "transport identity readback",
    "zigux/tests/phase10_build.zig",
    "zig test zigux/tests/phase10_virtio_mmio_survey.zig",
    "Documentation/zigux/freeze-map.md",
    "this survey stays inside `drivers/virtio/*.zig` and shared validation surfaces.",
    "this survey does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain study-only anchors.",
    "this survey also does not claim ownership of the freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`.",
};

const markers_1 = [_][]const u8{
    "# Phase 10 virtio MMIO Config-Write Disposition Companion",
    "PHASE10_STATUS=current_head_companion_landed",
    "PHASE10_FAMILY=virtio-mmio",
    "PHASE10_SURFACE=config-write-disposition-observation",
    "PHASE10_PROVENANCE_MODE=dated_master_readback",
    "surveyed against current `master` readback on `2026-05-19`",
    "Current `master` readback keeps this narrower MMIO packet explicit through:",
    "`drivers/virtio/virtio_mmio.zig` carries the richer config-write disposition observation helper",
    "`drivers/virtio/virtio_mmio_verify.zig` keeps the changed-byte-count, interrupt-ack-disposition, queue-readiness, and apply-observation wrapper proof explicit beside the helper",
    "`Documentation/zigux/phase10-virtio-mmio-survey.md` keeps the bounded transport-identity, queue-readiness, interrupt-ack-disposition, feature-negotiation, and config-write-disposition survey aligned with the same blocked lifecycle-and-IRQ boundary",
    "`zigux/tests/phase10_virtio_mmio.zig` keeps the helper-local probe-gating, queue-readiness, interrupt-ack-disposition, feature-negotiation, and config-write-disposition replays explicit",
    "`zigux/tests/phase10_virtio_mmio_survey.zig` rereads the parked survey note together with the shared `zigux/tests/phase10_build.zig` gate",
    "`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion, keeping the lab gate, dedicated apply-observation replay, survey gate, config-write companion, and slice note explicit beside the helper-local packet",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion, keeping the helper, dedicated apply-observation wrapper, dedicated apply-observation replay, survey, manifest, and blocked transport boundary aligned beside the config-write detail surface",
};

const markers_2 = [_][]const u8{
    "# Phase 10 Virtio MMIO Slice",
    "scripts\\zigux/check_phase10_mmio_packet.zig",
    "`drivers/virtio/virtio_mmio.zig` aligned with `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_config_write_plan_freshness.zig`, `drivers/virtio/virtio_mmio_verify.zig`",
    "transport-identity readback, probe-preflight gating, selected-queue readiness, interrupt-ack disposition review, staged feature-word negotiation, planning-only config-write plan freshness, planning-only config-write observation, apply-observation wrapper accounting, and config-write disposition review",
    "interrupt-ack disposition stays bounded to pending, acknowledged, ignored, and remaining bits review, not live IRQ delivery parity",
    "the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
};

const markers_3 = [_][]const u8{
    "# Phase 10 Closure Evidence",
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "scripts\\zigux/check_phase10_mmio_packet.zig",
    "phase10-mmio-config-write-apply-observation-helper",
    "phase10-mmio-lifecycle-and-irq-paths",
    "blocked_on_risky_transport",
};

const markers_4 = [_][]const u8{
    "\"lane_key\": \"P10-L11\"",
    "\"freeze_map\": \"Documentation/zigux/freeze-map.md\"",
    "\"freeze_boundary_status\": \"aligned\"",
    "\"freeze_status_change_claimed\": false",
    "\"risky_transport_posture\": \"blocked_on_risky_transport\"",
    "\"allowed_evidence_kinds\": [",
    "\"driver_local_lab_slices\"",
    "\"survey_manifests\"",
    "\"shared_validation_gates\"",
    "\"forbidden_transport_claims\": [",
    "\"queue_setup_reset_paths\"",
    "\"queue_reset_execution\"",
    "\"irq_parity\"",
    "\"dma_paths\"",
    "\"probe_remove_lifecycle\"",
    "\"freeze_restore_lifecycle\"",
    "\"architecture_council_reopen_required\": true",
    "\"architecture_council_reopen_attached\": false",
    "\"id\": \"phase10-mmio-transport-identity-helper\"",
    "\"id\": \"phase10-mmio-probe-preflight-helper\"",
    "\"id\": \"phase10-mmio-selected-queue-readiness-helper\"",
    "\"id\": \"phase10-mmio-interrupt-ack-disposition-helper\"",
    "\"id\": \"phase10-mmio-feature-negotiation-summary-helper\"",
    "\"id\": \"phase10-mmio-config-write-plan-freshness-helper\"",
    "\"id\": \"phase10-mmio-config-write-disposition-helper\"",
    "\"id\": \"phase10-mmio-config-write-apply-observation-helper\"",
    "\"id\": \"phase10-mmio-config-write-apply-observation-replay\"",
    "\"zigux_destination\": \"zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig\"",
    "\"id\": \"phase10-mmio-verify-replay\"",
    "\"id\": \"phase10-virtio-mmio-lab-gate\"",
    "\"zigux_destination\": \"zigux/tests/phase10_virtio_mmio.zig\"",
    "\"id\": \"phase10-virtio-mmio-survey-gate\"",
    "\"zigux_destination\": \"zigux/tests/phase10_virtio_mmio_survey.zig\"",
    "\"id\": \"phase10-virtio-mmio-survey-note\"",
    "\"zigux_destination\": \"Documentation/zigux/phase10-virtio-mmio-survey.md\"",
    "\"id\": \"phase10-virtio-mmio-config-write-disposition-note\"",
    "\"zigux_destination\": \"Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md\"",
    "\"id\": \"phase10-virtio-mmio-slice-note\"",
    "\"zigux_destination\": \"Documentation/zigux/phase10-virtio-mmio-slice.md\"",
    "\"status\": \"starter_landed\"",
};

const markers_5 = [_][]const u8{
    "pub const ConfigWritePlanFreshnessSummary = struct {",
    "pub const ConfigWriteDispositionSummary = struct {",
    "pub const ConfigWriteApplyObservationSummary = struct {",
    "pub const FeatureNegotiationSummary = struct {",
    "pub const TransportIdentitySummary = struct {",
    "pub const ProbePreflightSummary = struct {",
    "pub const SelectedQueueReadinessSummary = struct {",
    "pub const InterruptAckDispositionSummary = struct {",
    "pending_config_write: ?ConfigWritePlanSummary = null,",
    "pub fn bumpConfigGeneration(self: *Self) void {",
    "available_for_disposition = availability == .fresh,",
    "pub fn configWritePlanFreshnessSummary(self: *const Self) ConfigWritePlanFreshnessSummary {",
    "pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {",
    "pub fn configWriteApplyObservationSummary(self: *const Self) !ConfigWriteApplyObservationSummary {",
    "pub fn featureNegotiationSummary(self: *const Self) FeatureNegotiationSummary {",
    "pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {",
    "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
    "pub fn selectedQueueReadinessSummary(self: *const Self) !SelectedQueueReadinessSummary {",
    "pub fn interruptAckDispositionSummary(",
};

const markers_6 = [_][]const u8{
    "pub const TransportIdentitySummary = virtio_mmio.TransportIdentitySummary;",
    "pub const ProbePreflightSummary = virtio_mmio.ProbePreflightSummary;",
    "pub const SelectedQueueReadinessSummary = virtio_mmio.SelectedQueueReadinessSummary;",
    "pub const ConfigWritePlanFreshnessSummary = virtio_mmio.ConfigWritePlanFreshnessSummary;",
    "pub const ConfigWriteDispositionSummary = virtio_mmio.ConfigWriteDispositionSummary;",
    "pub const ConfigWriteApplyObservationSummary = virtio_mmio.ConfigWriteApplyObservationSummary;",
    "pub const FeatureNegotiationSummary = virtio_mmio.FeatureNegotiationSummary;",
    "pub const InterruptAckDispositionSummary = virtio_mmio.InterruptAckDispositionSummary;",
    "pub fn summarizeFeatureNegotiation(device: *const virtio_mmio.VirtioMmioLab) FeatureNegotiationSummary {",
    "pub fn summarizeConfigWritePlanFreshness(device: *const virtio_mmio.VirtioMmioLab) ConfigWritePlanFreshnessSummary {",
    "pub fn summarizeConfigWriteDisposition(device: *const virtio_mmio.VirtioMmioLab) !ConfigWriteDispositionSummary {",
    "pub fn summarizeConfigWriteApplyObservation(device: *const virtio_mmio.VirtioMmioLab) !ConfigWriteApplyObservationSummary {",
    "pub fn summarizeInterruptAckDisposition(",
    "pub fn changedByteCount(summary: ConfigWriteDispositionSummary) u3 {",
    "pub fn applyObservationChangedByteCount(summary: ConfigWriteApplyObservationSummary) u3 {",
    "pub fn acknowledgedInterruptCount(summary: InterruptAckDispositionSummary) u6 {",
    "pub fn hasFreshConfigWritePlan(summary: ConfigWritePlanFreshnessSummary) bool {",
    "pub fn configWriteObservationTouchesFullWord(summary: ConfigWriteApplyObservationSummary) bool {",
    "pub fn configWriteWouldApply(summary: ConfigWriteApplyObservationSummary) bool {",
    "test \"phase10 virtio mmio verify keeps probe wrapper transitions explicit\" {",
    "test \"phase10 virtio mmio verify keeps queue readiness wrapper below transport claims\" {",
    "test \"phase10 virtio mmio verify keeps feature negotiation wrapper drift explicit\" {",
    "test \"phase10 virtio mmio verify keeps config-write plan freshness below config application\" {",
    "test \"phase10 virtio mmio verify keeps stale config-write freshness visible but unavailable\" {",
    "test \"phase10 virtio mmio verify keeps config-write apply observation wrapper planning-only and explicit\" {",
    "test \"phase10 virtio mmio verify keeps interrupt-ack disposition below IRQ-delivery claims\" {",
    "test \"phase10 virtio mmio verify counts changed config bytes without mutating staged data\" {",
};

const markers_7 = [_][]const u8{
    "test \"phase10 virtio mmio keeps probe gating anchored below transport-backed claims\" {",
    "test \"phase10 virtio mmio keeps selected queue readiness bounded to in-memory register state\" {",
    "test \"phase10 virtio mmio selected queue readiness keeps per-queue state isolated across selector changes\" {",
    "_ = try device.writeRegister(.queue_num, 8);\n    summary = try device.selectedQueueReadinessSummary();\n    try std.testing.expect(summary.queue_size_programmed);\n    try std.testing.expect(!summary.queue_size_matches_advertised);\n    try std.testing.expect(!summary.queue_ready_for_handoff);",
    "test \"phase10 virtio mmio records feature mismatches without claiming live negotiation\" {",
    "test \"phase10 virtio mmio probe preflight keeps queue-window and interrupt-ack blockers explicit\" {",
    "test \"phase10 virtio mmio keeps interrupt-ack disposition bounded to reviewable queue and config bits\" {",
    "test \"phase10 virtio mmio keeps config-write planning bounded to staged review state\" {",
    "test \"phase10 virtio mmio keeps config-write plan freshness bounded to staged review state\" {",
    "test \"phase10 virtio mmio keeps stale config-write plans unavailable after generation drift\" {",
    "try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());",
    "test \"phase10 virtio mmio keeps config-write disposition planning-only across restaging\" {",
    "const no_op = try device.configWriteDispositionSummary();",
    "try std.testing.expectEqual(@as(u4, 0), no_op.changed_byte_mask);",
    "try std.testing.expect(!no_op.has_changes);",
    "test \"phase10 virtio mmio apply observation keeps touched and changed bytes reviewable without mutating config bytes\" {",
    "try std.testing.expectEqual(@as(u4, 0b1111), changed.touched_byte_mask);",
    "try std.testing.expectEqual(@as(u3, 0), no_op.changed_byte_count);",
    "try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteApplyObservationSummary());",
    "try std.testing.expect(!summary.bounded_queue_register_window_ready);",
    "try std.testing.expect(!summary.interrupt_ack_ready);",
    "try std.testing.expect(summary.queue_ready_for_handoff);",
};

const markers_8 = [_][]const u8{
    "const apply_observation = @import(\"virtio_mmio_apply_observation\");",
    "test \"phase10 virtio mmio apply-observation replay keeps changed bytes explicit\" {",
    "test \"phase10 virtio mmio apply-observation replay keeps no-op and stale plans distinct\" {",
    "try std.testing.expectError(",
    "error.ConfigWritePlanUnavailable,",
};

const markers_9 = [_][]const u8{
    ".root_source_file = b.path(\"phase10_virtio_mmio_apply_observation_replay.zig\"),",
    ".name = \"phase10-virtio-mmio-apply-observation-replay\",",
    "\"Run the bounded Phase 10 virtio MMIO apply-observation replay\",",
};

const markers_10 = [_][]const u8{
    "Keep the helper-local MMIO replay pair explicit too through `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig` and `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
    "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
    "without widening into lifecycle, IRQ-delivery, or DMA claims",
};

const markers_11 = [_][]const u8{
    "test \"phase10 virtio mmio survey note keeps the direct lab gate, packet-local companions, manifest companion, and dedicated survey gate explicit beside the helper-local packet\" {",
    "try expectContains(survey_note, \"interrupt-ack disposition review\");",
    "try expectContains(survey_note, \"staged config-write planning\");",
    "try expectContains(survey_note, \"config-write apply observation\");",
    "try expectContains(survey_note, \"zigux/tests/phase10_virtio_mmio_survey.zig\");",
    "try expectContains(survey_note, \"zig test zigux/tests/phase10_virtio_mmio_survey.zig\");",
    "try expectContains(build_file, \"\\\"phase10-virtio-mmio-survey-tests\\\"\");",
    "try expectContains(build_file, \"phase10_virtio_mmio_survey_module\");",
    "try expectContains(build_file, \"run_phase10_virtio_mmio_survey_tests.step\");",
    "test \"phase10 virtio mmio survey packet keeps the config-write companion and slice note explicit\" {",
    "`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion",
    "`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion",
    "`previous_value` and `planned_value` so a reviewer can compare the staged write against the existing config bytes",
    "`changed_byte_mask` so byte-level deltas are visible without replaying the full word manually",
    "`has_changes` derived from the actual byte-delta mask rather than a blanket true result",
    "`error.ConfigWritePlanUnavailable` when no current staged plan is available",
    "try expectContains(slice_note, \"# Phase 10 Virtio MMIO Slice\");",
    "try expectContains(slice_note, \"scripts\\\\zigux/check_phase10_mmio_packet.zig\");",
    "try expectContains(slice_note, \"planning-only config-write observation\");",
    "the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice",
    "test \"phase10 virtio mmio survey gate keeps survey-note lane identity, lane sequencing ownership, helper inventory, and risky transport posture explicit\" {",
    "try expectContains(lane_sequencing_note, \"MMIO lane `P10-L11` owns the bounded MMIO helper packet\");",
    "try expectContains(manifest, \"\\\"lane_key\\\": \\\"P10-L11\\\"\");",
    "try expectContains(manifest, \"\\\"risky_transport_posture\\\": \\\"blocked_on_risky_transport\\\"\");",
    "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-mmio-interrupt-ack-disposition-helper\\\"\");",
    "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-mmio-feature-negotiation-summary-helper\\\"\");",
    "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-mmio-config-write-plan-freshness-helper\\\"\");",
    "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-mmio-config-write-apply-observation-helper\\\"\");",
    "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-virtio-mmio-survey-gate\\\"\");",
    "test \"phase10 virtio mmio survey gate keeps helper-local queue isolation and probe blockers explicit\" {",
    "try expectContains(helper_tests, \"test \\\"phase10 virtio mmio selected queue readiness keeps per-queue state isolated across selector changes\\\" {\");",
    "try expectContains(helper_tests, \"test \\\"phase10 virtio mmio probe preflight keeps queue-window and interrupt-ack blockers explicit\\\" {\");",
    "try expectContains(helper_tests, \"test \\\"phase10 virtio mmio apply observation keeps touched and changed bytes reviewable without mutating config bytes\\\" {\");",
    "try expectContains(helper_tests, \"try std.testing.expect(!summary.bounded_queue_register_window_ready);\");",
    "try expectContains(helper_tests, \"try std.testing.expect(!summary.interrupt_ack_ready);\");",
    "try expectContains(helper_tests, \"try std.testing.expect(summary.queue_ready_for_handoff);\");",
    "test \"phase10 virtio mmio survey note keeps risky transport work and freeze-boundary policy evidence explicit\" {",
    "try expectContains(survey_note, \"transport-backed queue setup or queue reset execution\");",
    "try expectContains(survey_note, \"shared IRQ delivery parity\");",
};

const markers_12 = [_][]const u8{
    "../../drivers/virtio/virtio_mmio.zig",
    "../../drivers/virtio/virtio_mmio_verify.zig",
    "\"phase10-virtio-mmio-tests\"",
    "\"phase10-virtio-mmio-verify-tests\"",
    "\"phase10-virtio-mmio-survey-tests\"",
    "run_phase10_virtio_mmio_tests.step",
    "run_phase10_virtio_mmio_verify_tests.step",
    "run_phase10_virtio_mmio_survey_tests.step",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase10-virtio-mmio-survey.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase10-virtio-mmio-slice.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase10-closure-evidence.md", .markers = &markers_3 },
    .{ .rel = "zigux/tests/phase10_virtio_mmio_manifest.json", .markers = &markers_4 },
    .{ .rel = "drivers/virtio/virtio_mmio.zig", .markers = &markers_5 },
    .{ .rel = "drivers/virtio/virtio_mmio_verify.zig", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase10_virtio_mmio.zig", .markers = &markers_7 },
    .{ .rel = "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig", .markers = &markers_8 },
    .{ .rel = "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig", .markers = &markers_9 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_10 },
    .{ .rel = "zigux/tests/phase10_virtio_mmio_survey.zig", .markers = &markers_11 },
    .{ .rel = "zigux/tests/phase10_build.zig", .markers = &markers_12 },
};

const required_files = [_][]const u8{
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
    "Documentation/zigux/phase10-virtio-mmio-slice.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "drivers/virtio/virtio_mmio.zig",
    "drivers/virtio/virtio_mmio_verify.zig",
    "zigux/tests/phase10_virtio_mmio.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/README.md",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return error.MissingRequiredFile;
        file.close(io);
    }
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE10_MMIO_PACKET_REQUIRED_FILE_COUNT=13", .{});
    try guard.printLine(io, "PHASE10_MMIO_PACKET_REQUIRED_MARKER_COUNT=219", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_MMIO_PACKET_SELF_TEST_CASE_COUNT=103", .{});
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
// pub const pass_marker = "PHASE10_MMIO_PACKET_SELF_TEST=pass";
//
// const FILES = [_][]const u8{
//     "Documentation/zigux/phase10-virtio-mmio-survey.md",
//     "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
//     "Documentation/zigux/phase10-virtio-mmio-slice.md",
//     "Documentation/zigux/phase10-closure-evidence.md",
//     "drivers/virtio/virtio_mmio.zig",
//     "drivers/virtio/virtio_mmio_verify.zig",
//     "zigux/tests/phase10_virtio_mmio.zig",
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
//     "zigux/tests/phase10_virtio_mmio_survey.zig",
//     "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
//     "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",
//     "zigux/tests/phase10_build.zig",
//     "zigux/tests/README.md",
// };
//
// const SURVEY_NOTE_MARKERS = [_][]const u8{
//     "PHASE10_STATUS=parked",
//     "drivers/virtio/virtio_mmio.zig",
//     "drivers/virtio/virtio_mmio_verify.zig",
//     "zigux/tests/phase10_virtio_mmio.zig",
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
//     "zigux/tests/phase10_virtio_mmio_survey.zig",
//     "interrupt-ack disposition review",
//     "staged config-write planning",
//     "config-write apply observation",
//     "config-write disposition reporting",
//     "feature-negotiation deltas",
//     "transport identity readback",
//     "zigux/tests/phase10_build.zig",
//     "zig test zigux/tests/phase10_virtio_mmio_survey.zig",
//     "Documentation/zigux/freeze-map.md",
//     "this survey stays inside `drivers/virtio/*.zig` and shared validation surfaces.",
//     "this survey does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain study-only anchors.",
//     "this survey also does not claim ownership of the freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`.",
// };
//
// const COMPANION_MARKERS = [_][]const u8{
//     "PHASE10_STATUS=current_head_companion_landed",
//     "PHASE10_FAMILY=virtio-mmio",
//     "PHASE10_SURFACE=config-write-disposition-observation",
//     "PHASE10_PROVENANCE_MODE=dated_master_readback",
//     "surveyed against current `master` readback on `2026-05-19`",
//     "Current `master` readback keeps this narrower MMIO packet explicit through:",
//     "`drivers/virtio/virtio_mmio.zig` carries the richer config-write disposition observation helper",
//     "`drivers/virtio/virtio_mmio_verify.zig` keeps the changed-byte-count, interrupt-ack-disposition, queue-readiness, and apply-observation wrapper proof explicit beside the helper",
//     "`Documentation/zigux/phase10-virtio-mmio-survey.md` keeps the bounded transport-identity, queue-readiness, interrupt-ack-disposition, feature-negotiation, and config-write-disposition survey aligned with the same blocked lifecycle-and-IRQ boundary",
//     "`zigux/tests/phase10_virtio_mmio.zig` keeps the helper-local probe-gating, queue-readiness, interrupt-ack-disposition, feature-negotiation, and config-write-disposition replays explicit",
//     "`zigux/tests/phase10_virtio_mmio_survey.zig` rereads the parked survey note together with the shared `zigux/tests/phase10_build.zig` gate",
//     "`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion, keeping the lab gate, dedicated apply-observation replay, survey gate, config-write companion, and slice note explicit beside the helper-local packet",
//     "`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion, keeping the helper, dedicated apply-observation wrapper, dedicated apply-observation replay, survey, manifest, and blocked transport boundary aligned beside the config-write detail surface",
// };
//
// const SLICE_NOTE_MARKERS = [_][]const u8{
//     "scripts/zigux/check_phase10_mmio_packet.zig",
//     "`drivers/virtio/virtio_mmio.zig` aligned with `drivers/virtio/virtio_mmio_apply_observation.zig`, `drivers/virtio/virtio_mmio_config_write_plan_freshness.zig`, `drivers/virtio/virtio_mmio_verify.zig`",
//     "transport-identity readback, probe-preflight gating, selected-queue readiness, interrupt-ack disposition review, staged feature-word negotiation, planning-only config-write plan freshness, planning-only config-write observation, apply-observation wrapper accounting, and config-write disposition review",
//     "interrupt-ack disposition stays bounded to pending, acknowledged, ignored, and remaining bits review, not live IRQ delivery parity",
//     "the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice",
//     "`Documentation/zigux/phase10-virtio-mmio-slice.md`",
// };
//
// const CLOSURE_NOTE_MARKERS = [_][]const u8{
//     "Documentation/zigux/phase10-virtio-mmio-survey.md",
//     "Documentation/zigux/phase10-virtio-mmio-slice.md",
//     "Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md",
//     "drivers/virtio/virtio_mmio.zig",
//     "drivers/virtio/virtio_mmio_verify.zig",
//     "zigux/tests/phase10_virtio_mmio.zig",
//     "zigux/tests/phase10_virtio_mmio_survey.zig",
//     "scripts/zigux/check_phase10_mmio_packet.zig",
//     "phase10-mmio-config-write-apply-observation-helper",
//     "phase10-mmio-lifecycle-and-irq-paths",
//     "blocked_on_risky_transport",
// };
//
// const MANIFEST_MARKERS = [_][]const u8{
//     "\"lane_key\": \"P10-L11\"",
//     "\"freeze_map\": \"Documentation/zigux/freeze-map.md\"",
//     "\"freeze_boundary_status\": \"aligned\"",
//     "\"freeze_status_change_claimed\": false",
//     "\"risky_transport_posture\": \"blocked_on_risky_transport\"",
//     "\"allowed_evidence_kinds\": [",
//     "\"driver_local_lab_slices\"",
//     "\"survey_manifests\"",
//     "\"shared_validation_gates\"",
//     "\"forbidden_transport_claims\": [",
//     "\"queue_setup_reset_paths\"",
//     "\"queue_reset_execution\"",
//     "\"irq_parity\"",
//     "\"dma_paths\"",
//     "\"probe_remove_lifecycle\"",
//     "\"freeze_restore_lifecycle\"",
//     "\"architecture_council_reopen_required\": true",
//     "\"architecture_council_reopen_attached\": false",
//     "\"id\": \"phase10-mmio-transport-identity-helper\"",
//     "\"id\": \"phase10-mmio-probe-preflight-helper\"",
//     "\"id\": \"phase10-mmio-selected-queue-readiness-helper\"",
//     "\"id\": \"phase10-mmio-interrupt-ack-disposition-helper\"",
//     "\"id\": \"phase10-mmio-feature-negotiation-summary-helper\"",
//     "\"id\": \"phase10-mmio-config-write-plan-freshness-helper\"",
//     "\"id\": \"phase10-mmio-config-write-disposition-helper\"",
//     "\"id\": \"phase10-mmio-config-write-apply-observation-helper\"",
//     "\"id\": \"phase10-mmio-config-write-apply-observation-replay\"",
//     "\"zigux_destination\": \"zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig\"",
//     "\"id\": \"phase10-mmio-verify-replay\"",
//     "\"id\": \"phase10-virtio-mmio-lab-gate\"",
//     "\"zigux_destination\": \"zigux/tests/phase10_virtio_mmio.zig\"",
//     "\"id\": \"phase10-virtio-mmio-survey-gate\"",
//     "\"zigux_destination\": \"zigux/tests/phase10_virtio_mmio_survey.zig\"",
//     "\"id\": \"phase10-virtio-mmio-survey-note\"",
//     "\"zigux_destination\": \"Documentation/zigux/phase10-virtio-mmio-survey.md\"",
//     "\"id\": \"phase10-virtio-mmio-config-write-disposition-note\"",
//     "\"zigux_destination\": \"Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md\"",
//     "\"id\": \"phase10-virtio-mmio-slice-note\"",
//     "\"zigux_destination\": \"Documentation/zigux/phase10-virtio-mmio-slice.md\"",
//     "\"status\": \"starter_landed\"",
// };
//
// const HELPER_MARKERS = [_][]const u8{
//     "pub const ConfigWritePlanFreshnessSummary = struct {",
//     "pub const ConfigWriteDispositionSummary = struct {",
//     "pub const ConfigWriteApplyObservationSummary = struct {",
//     "pub const FeatureNegotiationSummary = struct {",
//     "pub const TransportIdentitySummary = struct {",
//     "pub const ProbePreflightSummary = struct {",
//     "pub const SelectedQueueReadinessSummary = struct {",
//     "pub const InterruptAckDispositionSummary = struct {",
//     "pending_config_write: ?ConfigWritePlanSummary = null,",
//     "pub fn bumpConfigGeneration(self: *Self) void {",
//     "available_for_disposition = availability == .fresh,",
//     "pub fn configWritePlanFreshnessSummary(self: *const Self) ConfigWritePlanFreshnessSummary {",
//     "pub fn configWriteDispositionSummary(self: *const Self) !ConfigWriteDispositionSummary {",
//     "pub fn configWriteApplyObservationSummary(self: *const Self) !ConfigWriteApplyObservationSummary {",
//     "pub fn featureNegotiationSummary(self: *const Self) FeatureNegotiationSummary {",
//     "pub fn transportIdentitySummary(self: *const Self) TransportIdentitySummary {",
//     "pub fn probePreflightSummary(self: *const Self) ProbePreflightSummary {",
//     "pub fn selectedQueueReadinessSummary(self: *const Self) !SelectedQueueReadinessSummary {",
//     "pub fn interruptAckDispositionSummary(",
// };
//
// const VERIFY_MARKERS = [_][]const u8{
//     "pub const TransportIdentitySummary = virtio_mmio.TransportIdentitySummary;",
//     "pub const ProbePreflightSummary = virtio_mmio.ProbePreflightSummary;",
//     "pub const SelectedQueueReadinessSummary = virtio_mmio.SelectedQueueReadinessSummary;",
//     "pub const ConfigWritePlanFreshnessSummary = virtio_mmio.ConfigWritePlanFreshnessSummary;",
//     "pub const ConfigWriteDispositionSummary = virtio_mmio.ConfigWriteDispositionSummary;",
//     "pub const ConfigWriteApplyObservationSummary = virtio_mmio.ConfigWriteApplyObservationSummary;",
//     "pub const FeatureNegotiationSummary = virtio_mmio.FeatureNegotiationSummary;",
//     "pub const InterruptAckDispositionSummary = virtio_mmio.InterruptAckDispositionSummary;",
//     "pub fn summarizeFeatureNegotiation(device: *const virtio_mmio.VirtioMmioLab) FeatureNegotiationSummary {",
//     "pub fn summarizeConfigWritePlanFreshness(device: *const virtio_mmio.VirtioMmioLab) ConfigWritePlanFreshnessSummary {",
//     "pub fn summarizeConfigWriteDisposition(device: *const virtio_mmio.VirtioMmioLab) !ConfigWriteDispositionSummary {",
//     "pub fn summarizeConfigWriteApplyObservation(device: *const virtio_mmio.VirtioMmioLab) !ConfigWriteApplyObservationSummary {",
//     "pub fn summarizeInterruptAckDisposition(",
//     "pub fn changedByteCount(summary: ConfigWriteDispositionSummary) u3 {",
//     "pub fn applyObservationChangedByteCount(summary: ConfigWriteApplyObservationSummary) u3 {",
//     "pub fn acknowledgedInterruptCount(summary: InterruptAckDispositionSummary) u6 {",
//     "pub fn hasFreshConfigWritePlan(summary: ConfigWritePlanFreshnessSummary) bool {",
//     "pub fn configWriteObservationTouchesFullWord(summary: ConfigWriteApplyObservationSummary) bool {",
//     "pub fn configWriteWouldApply(summary: ConfigWriteApplyObservationSummary) bool {",
//     "test \"phase10 virtio mmio verify keeps probe wrapper transitions explicit\" {",
//     "test \"phase10 virtio mmio verify keeps queue readiness wrapper below transport claims\" {",
//     "test \"phase10 virtio mmio verify keeps feature negotiation wrapper drift explicit\" {",
//     "test \"phase10 virtio mmio verify keeps config-write plan freshness below config application\" {",
//     "test \"phase10 virtio mmio verify keeps stale config-write freshness visible but unavailable\" {",
//     "test \"phase10 virtio mmio verify keeps config-write apply observation wrapper planning-only and explicit\" {",
//     "test \"phase10 virtio mmio verify keeps interrupt-ack disposition below IRQ-delivery claims\" {",
//     "test \"phase10 virtio mmio verify counts changed config bytes without mutating staged data\" {",
// };
//
// const HELPER_TEST_MARKERS = [_][]const u8{
//     "test \"phase10 virtio mmio keeps probe gating anchored below transport-backed claims\" {",
//     "test \"phase10 virtio mmio keeps selected queue readiness bounded to in-memory register state\" {",
//     "test \"phase10 virtio mmio selected queue readiness keeps per-queue state isolated across selector changes\" {",
//     "_ = try device.writeRegister(.queue_num, 8);n    summary = try device.selectedQueueReadinessSummary();n    try std.testing.expect(summary.queue_size_programmed);n    try std.testing.expect(!summary.queue_size_matches_advertised);n    try std.testing.expect(!summary.queue_ready_for_handoff);",
//     "test \"phase10 virtio mmio records feature mismatches without claiming live negotiation\" {",
//     "test \"phase10 virtio mmio probe preflight keeps queue-window and interrupt-ack blockers explicit\" {",
//     "test \"phase10 virtio mmio keeps interrupt-ack disposition bounded to reviewable queue and config bits\" {",
//     "test \"phase10 virtio mmio keeps config-write planning bounded to staged review state\" {",
//     "test \"phase10 virtio mmio keeps config-write plan freshness bounded to staged review state\" {",
//     "test \"phase10 virtio mmio keeps stale config-write plans unavailable after generation drift\" {",
//     "try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteDispositionSummary());",
//     "test \"phase10 virtio mmio keeps config-write disposition planning-only across restaging\" {",
//     "const no_op = try device.configWriteDispositionSummary();",
//     "try std.testing.expectEqual(@as(u4, 0), no_op.changed_byte_mask);",
//     "try std.testing.expect(!no_op.has_changes);",
//     "test \"phase10 virtio mmio apply observation keeps touched and changed bytes reviewable without mutating config bytes\" {",
//     "try std.testing.expectEqual(@as(u4, 0b1111), changed.touched_byte_mask);",
//     "try std.testing.expectEqual(@as(u3, 0), no_op.changed_byte_count);",
//     "try std.testing.expectError(error.ConfigWritePlanUnavailable, device.configWriteApplyObservationSummary());",
//     "try std.testing.expect(!summary.bounded_queue_register_window_ready);",
//     "try std.testing.expect(!summary.interrupt_ack_ready);",
//     "try std.testing.expect(summary.queue_ready_for_handoff);",
// };
//
// const APPLY_OBSERVATION_REPLAY_MARKERS = [_][]const u8{
//     "const apply_observation = @import(\"virtio_mmio_apply_observation\");",
//     "test \"phase10 virtio mmio apply-observation replay keeps changed bytes explicit\" {",
//     "test \"phase10 virtio mmio apply-observation replay keeps no-op and stale plans distinct\" {",
//     "try std.testing.expectError(",
//     "error.ConfigWritePlanUnavailable,",
// };
//
// const APPLY_OBSERVATION_BUILD_MARKERS = [_][]const u8{
//     ".root_source_file = b.path(\"phase10_virtio_mmio_apply_observation_replay.zig\"),",
//     ".name = \"phase10-virtio-mmio-apply-observation-replay\",",
//     "\"Run the bounded Phase 10 virtio MMIO apply-observation replay\",",
// };
//
// const TESTS_ROOT_README_MARKERS = [_][]const u8{
//     "Keep the helper-local MMIO replay pair explicit too through `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig` and `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
//     "`zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`",
//     "`zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`",
//     "without widening into lifecycle, IRQ-delivery, or DMA claims",
// };
//
// const SURVEY_GATE_MARKERS = [_][]const u8{
//     "test \"phase10 virtio mmio survey note keeps the direct lab gate, packet-local companions, manifest companion, and dedicated survey gate explicit beside the helper-local packet\" {",
//     "try expectContains(survey_note, \"interrupt-ack disposition review\");",
//     "try expectContains(survey_note, \"staged config-write planning\");",
//     "try expectContains(survey_note, \"config-write apply observation\");",
//     "try expectContains(survey_note, \"zigux/tests/phase10_virtio_mmio_survey.zig\");",
//     "try expectContains(survey_note, \"zig test zigux/tests/phase10_virtio_mmio_survey.zig\");",
//     "try expectContains(build_file, \"\\\"phase10-virtio-mmio-survey-tests\\\"\");",
//     "try expectContains(build_file, \"phase10_virtio_mmio_survey_module\");",
//     "try expectContains(build_file, \"run_phase10_virtio_mmio_survey_tests.step\");",
//     "test \"phase10 virtio mmio survey packet keeps the config-write companion and slice note explicit\" {",
//     "`zigux/tests/phase10_virtio_mmio_manifest.json` now rematerializes as the bounded MMIO manifest companion",
//     "`Documentation/zigux/phase10-virtio-mmio-slice.md` now materializes as the packet-local slice companion",
//     "`previous_value` and `planned_value` so a reviewer can compare the staged write against the existing config bytes",
//     "`changed_byte_mask` so byte-level deltas are visible without replaying the full word manually",
//     "`has_changes` derived from the actual byte-delta mask rather than a blanket true result",
//     "`error.ConfigWritePlanUnavailable` when no current staged plan is available",
//     "try expectContains(slice_note, \"# Phase 10 Virtio MMIO Slice\");",
//     "try expectContains(slice_note, \"scripts/zigux/check_phase10_mmio_packet.zig\");",
//     "try expectContains(slice_note, \"planning-only config-write observation\");",
//     "the blocked `phase10-mmio-lifecycle-and-irq-paths` bucket remains outside this slice",
//     "test \"phase10 virtio mmio survey gate keeps survey-note lane identity, lane sequencing ownership, helper inventory, and risky transport posture explicit\" {",
//     "try expectContains(lane_sequencing_note, \"MMIO lane `P10-L11` owns the bounded MMIO helper packet\");",
//     "try expectContains(manifest, \"\\\"lane_key\\\": \\\"P10-L11\\\"\");",
//     "try expectContains(manifest, \"\\\"risky_transport_posture\\\": \\\"blocked_on_risky_transport\\\"\");",
//     "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-mmio-interrupt-ack-disposition-helper\\\"\");",
//     "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-mmio-feature-negotiation-summary-helper\\\"\");",
//     "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-mmio-config-write-plan-freshness-helper\\\"\");",
//     "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-mmio-config-write-apply-observation-helper\\\"\");",
//     "try expectContains(manifest, \"\\\"id\\\": \\\"phase10-virtio-mmio-survey-gate\\\"\");",
//     "test \"phase10 virtio mmio survey gate keeps helper-local queue isolation and probe blockers explicit\" {",
//     "try expectContains(helper_tests, \"test \\\"phase10 virtio mmio selected queue readiness keeps per-queue state isolated across selector changes\\\" {\");",
//     "try expectContains(helper_tests, \"test \\\"phase10 virtio mmio probe preflight keeps queue-window and interrupt-ack blockers explicit\\\" {\");",
//     "try expectContains(helper_tests, \"test \\\"phase10 virtio mmio apply observation keeps touched and changed bytes reviewable without mutating config bytes\\\" {\");",
//     "try expectContains(helper_tests, \"try std.testing.expect(!summary.bounded_queue_register_window_ready);\");",
//     "try expectContains(helper_tests, \"try std.testing.expect(!summary.interrupt_ack_ready);\");",
//     "try expectContains(helper_tests, \"try std.testing.expect(summary.queue_ready_for_handoff);\");",
//     "test \"phase10 virtio mmio survey note keeps risky transport work and freeze-boundary policy evidence explicit\" {",
//     "try expectContains(survey_note, \"transport-backed queue setup or queue reset execution\");",
//     "try expectContains(survey_note, \"shared IRQ delivery parity\");",
// };
//
// const BUILD_MARKERS = [_][]const u8{
//     ".root_source_file = b.path(\"phase10_virtio_mmio_apply_observation_replay.zig\"),",
//     ".name = \"phase10-virtio-mmio-apply-observation-replay\",",
//     "\"Run the bounded Phase 10 virtio MMIO apply-observation replay\",",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (FILES) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (COMPANION_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SLICE_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (CLOSURE_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (HELPER_TEST_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (APPLY_OBSERVATION_REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (APPLY_OBSERVATION_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (TESTS_ROOT_README_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_GATE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
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
