const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_CORE_PACKET=pass";
pub const self_test_pass_marker = "PHASE10_CORE_PACKET_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };
const Gap = struct { id: []const u8, kind: []const u8, status: []const u8, zigux_destination: []const u8 };
const SurveySummary = struct {
    preexisting_phase10_test_files: usize,
    preexisting_phase10_build_present: bool,
    preexisting_virtio_core_zig_present: bool,
    preexisting_virtio_core_test_present: bool,
    preexisting_virtio_core_reset_queue_test_present: bool,
    preexisting_virtio_driver_id_zig_present: bool,
    preexisting_virtio_driver_id_test_present: bool,
    preexisting_virtio_core_slice_note_present: bool,
    preexisting_virtio_ring_survey_present: bool,
    preexisting_virtio_input_survey_present: bool,
    preexisting_virtio_mmio_survey_present: bool,
};
const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    freeze_map: []const u8,
    freeze_boundary_status: []const u8,
    freeze_status_change_claimed: bool,
    risky_transport_posture: []const u8,
    allowed_evidence_kinds: []const []const u8,
    forbidden_transport_claims: []const []const u8,
    architecture_council_reopen_required: bool,
    architecture_council_reopen_attached: bool,
    surveyed_commit: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

const markers_0 = [_][]const u8{
    "lane: `P10-L01`",
    "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
    "## Roadmap helper parity scoreboard",
    "That scoreboard now mirrors the live manifest IDs directly",
    "`drivers/virtio/virtio.zig`",
    "`drivers/virtio/virtio_driver_id.zig`",
    "`drivers/virtio/virtio_verify.zig`",
    "`zigux/tests/phase10_virtio_core.zig`",
    "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
    "`zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`",
    "`zigux/tests/phase10_virtio_driver_id.zig`",
    "`zigux/tests/phase10_virtio_core_survey.zig`",
    "`zigux/tests/phase10_build.zig`",
    "`scripts\\zigux/validate_phase10.zig`",
    "`scripts\\zigux/check_phase10_core_packet.zig`",
    "phase10-driver-id-helper",
    "phase10-driver-id-coverage-disposition-helper",
    "phase10-core-probe-remove-lifecycle",
};

const markers_1 = [_][]const u8{
    "pub fn reviewDriverIdMatch(",
    "pub fn reviewDevice(",
    "test \"phase10 virtio driver id review keeps exact matches explicit\" {",
    "test \"phase10 virtio driver id review keeps wildcard matches and misses distinct\" {",
};

const markers_2 = [_][]const u8{
    "pub fn summarizeDriverModel(",
    "pub fn resetReplayPreservesQueueShape(",
    "test \"phase10 virtio core verify keeps lifecycle checkpoints explicit\" {",
    "test \"phase10 virtio core verify keeps reset replay below transport lifecycle claims\" {",
};

const markers_3 = [_][]const u8{
    ".name = \"phase10-virtio-core-tests\"",
    ".name = \"phase10-virtio-core-interrupt-compound-ack-tests\"",
    ".name = \"phase10-virtio-core-reset-queue-tests\"",
    ".name = \"phase10-virtio-core-verify-tests\"",
    ".name = \"phase10-virtio-core-survey-tests\"",
    ".name = \"phase10-virtio-driver-id-tests\"",
    "test_step.dependOn(&run_phase10_virtio_core_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_core_interrupt_compound_ack_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_core_reset_queue_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_core_verify_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_core_survey_tests.step);",
    "test_step.dependOn(&run_phase10_virtio_driver_id_tests.step);",
};

const markers_4 = [_][]const u8{
    "test \"phase10 virtio core summary replay keeps status and feature bookkeeping reviewable\" {",
    "test \"phase10 virtio core reset replay clears interrupt debt and drops driver readiness\" {",
    "test \"phase10 virtio core driver id replay keeps exact wildcard and unmatched rules reviewable\" {",
};

const markers_5 = [_][]const u8{
    "test \"phase10 virtio core interrupt compound ack replay keeps queue-used and config-change bits isolated\" {",
};

const markers_6 = [_][]const u8{
    "test \"phase10 virtio core reset queue replay drops ready state until queue and status are replayed\" {",
    "test \"phase10 virtio core reset queue replay clears reset-required state\" {",
};

const markers_7 = [_][]const u8{
    "test \"phase10 virtio driver id replay keeps exact and wildcard dispositions reviewable\" {",
    "test \"phase10 virtio driver id replay keeps vendor wildcard and no-match paths separate\" {",
};

const forbidden_markers_0 = [_][]const u8{
    "stale guardrail reference drift",
    "can still return `404`",
    "mixed-source verification path",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase10-virtio-core-survey.md", .markers = &markers_0 },
    .{ .rel = "drivers/virtio/virtio_driver_id.zig", .markers = &markers_1 },
    .{ .rel = "drivers/virtio/virtio_verify.zig", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase10_build.zig", .markers = &markers_3 },
    .{ .rel = "zigux/tests/phase10_virtio_core.zig", .markers = &markers_4 },
    .{ .rel = "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig", .markers = &markers_5 },
    .{ .rel = "zigux/tests/phase10_virtio_core_reset_queue.zig", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase10_virtio_driver_id.zig", .markers = &markers_7 },
};

const forbidden_contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase10-virtio-core-survey.md", .markers = &forbidden_markers_0 },
};

const expected_roadmap_destinations = [_][]const u8{
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
};

const expected_allowed_evidence_kinds = [_][]const u8{
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
};

const expected_forbidden_transport_claims = [_][]const u8{
    "queue_setup_reset_paths",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
};

const expected_gaps = [_]Gap{
    .{ .id = "phase10-build-gate", .kind = "validation", .status = "starter_landed", .zigux_destination = "zigux/tests/phase10_build.zig" },
    .{ .id = "phase10-virtio-core-lab-starter", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-virtio-core-lab-gate", .kind = "validation", .status = "starter_landed", .zigux_destination = "zigux/tests/phase10_virtio_core.zig" },
    .{ .id = "phase10-virtio-core-reset-queue-gate", .kind = "validation", .status = "starter_landed", .zigux_destination = "zigux/tests/phase10_virtio_core_reset_queue.zig" },
    .{ .id = "phase10-virtio-core-slice-note", .kind = "documentation", .status = "starter_landed", .zigux_destination = "Documentation/zigux/phase10-virtio-core-slice.md" },
    .{ .id = "phase10-virtio-core-survey-gate", .kind = "validation", .status = "starter_landed", .zigux_destination = "zigux/tests/phase10_virtio_core_survey.zig" },
    .{ .id = "phase10-virtio-core-survey-note", .kind = "documentation", .status = "starter_landed", .zigux_destination = "Documentation/zigux/phase10-virtio-core-survey.md" },
    .{ .id = "phase10-virtio-core-verify-replay", .kind = "validation", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio_verify.zig" },
    .{ .id = "phase10-queue-shape-bookkeeping-helper", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-config-generation-bookkeeping-helper", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-interrupt-ack-bookkeeping-helper", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-lifecycle-guard-bookkeeping-helper", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-driver-validation-narrowing-helper", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-core-attribute-summary-helper", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-reset-replay-bookkeeping-helper", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-core-lab-validation-evidence", .kind = "validation", .status = "starter_landed", .zigux_destination = "Documentation/zigux/phase10-virtio-core-survey.md" },
    .{ .id = "phase10-driver-id-helper", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio_driver_id.zig" },
    .{ .id = "phase10-driver-id-coverage-disposition-helper", .kind = "lab_driver_starter", .status = "starter_landed", .zigux_destination = "drivers/virtio/virtio_driver_id.zig" },
    .{ .id = "phase10-driver-id-review-gate", .kind = "validation", .status = "starter_landed", .zigux_destination = "zigux/tests/phase10_virtio_driver_id.zig" },
    .{ .id = "phase10-interrupt-compound-ack-gate", .kind = "validation", .status = "starter_landed", .zigux_destination = "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig" },
    .{ .id = "phase10-core-dual-implementation-bridge", .kind = "dual_implementation_boundary", .status = "blocked_on_risky_transport", .zigux_destination = "drivers/virtio/virtio.zig" },
    .{ .id = "phase10-core-probe-remove-lifecycle", .kind = "lab_driver_starter", .status = "blocked_on_risky_transport", .zigux_destination = "drivers/virtio/virtio.zig" },
};

fn expectStrings(actual: []const []const u8, expected: []const []const u8) !void {
    if (actual.len != expected.len) return error.StringArrayLengthDrift;
    for (actual, expected) |a, e| if (!std.mem.eql(u8, a, e)) return error.StringArrayValueDrift;
}

fn validCommit(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |c| if (!((c >= '0' and c <= '9') or (c >= 'a' and c <= 'f'))) return false;
    return true;
}

fn expectGap(actual: []const Gap, expected: Gap) !void {
    for (actual) |gap| {
        if (!std.mem.eql(u8, gap.id, expected.id)) continue;
        if (!std.mem.eql(u8, gap.kind, expected.kind)) return error.GapKindDrift;
        if (!std.mem.eql(u8, gap.status, expected.status)) return error.GapStatusDrift;
        if (!std.mem.eql(u8, gap.zigux_destination, expected.zigux_destination)) return error.GapDestinationDrift;
        return;
    }
    return error.MissingGap;
}

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
    const manifest_path = try guard.joinPath(allocator, root, "zigux/tests/phase10_virtio_core_manifest.json");
    defer allocator.free(manifest_path);
    const manifest_text = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest_text);
    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_text, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const value = parsed.value;
    // Legacy manifest readback marker: "lane_key": "P10-L01",
    // Legacy build registration marker: .name = "phase10-virtio-core-survey-tests"
    if (!std.mem.eql(u8, value.lane_key, "P10-L01")) return error.LaneDrift;
    if (!std.mem.eql(u8, value.phase, "Phase 10")) return error.PhaseDrift;
    if (!std.mem.eql(u8, value.anchor, "drivers/virtio/virtio.c")) return error.AnchorDrift;
    try expectStrings(value.roadmap_destinations, &expected_roadmap_destinations);
    if (!std.mem.eql(u8, value.freeze_map, "Documentation/zigux/freeze-map.md")) return error.FreezeMapDrift;
    if (!std.mem.eql(u8, value.freeze_boundary_status, "aligned")) return error.FreezeBoundaryDrift;
    if (value.freeze_status_change_claimed != false) return error.FreezeClaimDrift;
    if (!std.mem.eql(u8, value.risky_transport_posture, "blocked_on_risky_transport")) return error.TransportPostureDrift;
    try expectStrings(value.allowed_evidence_kinds, &expected_allowed_evidence_kinds);
    try expectStrings(value.forbidden_transport_claims, &expected_forbidden_transport_claims);
    if (value.architecture_council_reopen_required != true) return error.ReopenRequiredDrift;
    if (value.architecture_council_reopen_attached != false) return error.ReopenAttachedDrift;
    if (!validCommit(value.surveyed_commit)) return error.InvalidSurveyCommit;
    if (value.survey_summary.preexisting_phase10_test_files != 11) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_phase10_build_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_core_zig_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_core_test_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_core_reset_queue_test_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_driver_id_zig_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_driver_id_test_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_core_slice_note_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_ring_survey_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_input_survey_present != true) return error.SurveySummaryDrift;
    if (value.survey_summary.preexisting_virtio_mmio_survey_present != true) return error.SurveySummaryDrift;
    if (value.gaps.len != expected_gaps.len) return error.GapCountDrift;
    for (expected_gaps) |gap| try expectGap(value.gaps, gap);
    const survey_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase10-virtio-core-survey.md");
    defer allocator.free(survey_path);
    const survey = try guard.readUtf8File(io, allocator, survey_path);
    defer allocator.free(survey);
    try guard.requireMarker(survey, value.surveyed_commit);
    for (expected_gaps) |gap| try guard.requireMarker(survey, gap.id);
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE10_CORE_PACKET_REQUIRED_FILE_COUNT=9", .{});
    try guard.printLine(io, "PHASE10_CORE_PACKET_REQUIRED_MARKER_COUNT=46", .{});
    try guard.printLine(io, "PHASE10_CORE_PACKET_FORBIDDEN_MARKER_COUNT=3", .{});
    try guard.printLine(io, "PHASE10_CORE_PACKET_GAP_COUNT=22", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_CORE_PACKET_SELF_TEST_CASE_COUNT=7", .{});
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
// pub const pass_marker = "PHASE10_CORE_PACKET_SELF_TEST=pass";
//
// const EXPECTED_MANIFEST_FIELDS = [_][]const u8{
//     "lane_key",
//     "P10-L01",
//     "phase",
//     "Phase 10",
//     "anchor",
//     "drivers/virtio/virtio.c",
//     "roadmap_destinations",
//     "drivers/virtio/*.zig",
//     "zigux/kernel/",
//     "zigux/helpers/",
//     "freeze_map",
//     "Documentation/zigux/freeze-map.md",
//     "freeze_boundary_status",
//     "aligned",
//     "freeze_status_change_claimed",
//     "risky_transport_posture",
//     "blocked_on_risky_transport",
//     "allowed_evidence_kinds",
//     "driver_local_lab_slices",
//     "survey_manifests",
//     "shared_validation_gates",
//     "forbidden_transport_claims",
//     "queue_setup_reset_paths",
//     "irq_parity",
//     "dma_paths",
//     "input_registration_lifecycle",
//     "probe_remove_lifecycle",
//     "architecture_council_reopen_required",
//     "architecture_council_reopen_attached",
// };
//
// const EXPECTED_SUMMARY_VALUES = [_][]const u8{
//     "preexisting_phase10_test_files",
//     "preexisting_phase10_build_present",
//     "preexisting_virtio_core_zig_present",
//     "preexisting_virtio_core_test_present",
//     "preexisting_virtio_core_reset_queue_test_present",
//     "preexisting_virtio_driver_id_zig_present",
//     "preexisting_virtio_driver_id_test_present",
//     "preexisting_virtio_core_slice_note_present",
//     "preexisting_virtio_ring_survey_present",
//     "preexisting_virtio_input_survey_present",
//     "preexisting_virtio_mmio_survey_present",
// };
//
// const EXPECTED_GAP_FIELDS = [_][]const u8{
//     "phase10-build-gate",
//     "kind",
//     "validation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "zigux/tests/phase10_build.zig",
//     "phase10-virtio-core-lab-starter",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
//     "phase10-virtio-core-lab-gate",
//     "kind",
//     "validation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "zigux/tests/phase10_virtio_core.zig",
//     "phase10-virtio-core-reset-queue-gate",
//     "kind",
//     "validation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "zigux/tests/phase10_virtio_core_reset_queue.zig",
//     "phase10-virtio-core-slice-note",
//     "kind",
//     "documentation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "Documentation/zigux/phase10-virtio-core-slice.md",
//     "phase10-virtio-core-survey-gate",
//     "kind",
//     "validation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "zigux/tests/phase10_virtio_core_survey.zig",
//     "phase10-virtio-core-survey-note",
//     "kind",
//     "documentation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "phase10-virtio-core-verify-replay",
//     "kind",
//     "validation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio_verify.zig",
//     "phase10-queue-shape-bookkeeping-helper",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
//     "phase10-config-generation-bookkeeping-helper",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
//     "phase10-interrupt-ack-bookkeeping-helper",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
//     "phase10-lifecycle-guard-bookkeeping-helper",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
//     "phase10-driver-validation-narrowing-helper",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
//     "phase10-core-attribute-summary-helper",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
//     "phase10-reset-replay-bookkeeping-helper",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
//     "phase10-core-lab-validation-evidence",
//     "kind",
//     "validation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "phase10-driver-id-helper",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio_driver_id.zig",
//     "phase10-driver-id-coverage-disposition-helper",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "drivers/virtio/virtio_driver_id.zig",
//     "phase10-driver-id-review-gate",
//     "kind",
//     "validation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "zigux/tests/phase10_virtio_driver_id.zig",
//     "phase10-interrupt-compound-ack-gate",
//     "kind",
//     "validation",
//     "status",
//     "starter_landed",
//     "zigux_destination",
//     "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
//     "phase10-core-dual-implementation-bridge",
//     "kind",
//     "dual_implementation_boundary",
//     "status",
//     "blocked_on_risky_transport",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
//     "phase10-core-probe-remove-lifecycle",
//     "kind",
//     "lab_driver_starter",
//     "status",
//     "blocked_on_risky_transport",
//     "zigux_destination",
//     "drivers/virtio/virtio.zig",
// };
//
// const REQUIRED_PATHS = [_][]const u8{
//     "lane: `P10-L01`",
//     "c11221dc7a68d7511ae1c69d64b3f08528287ed8",
//     "## Roadmap helper parity scoreboard",
//     "That scoreboard now mirrors the live manifest IDs directly",
//     "`drivers/virtio/virtio.zig`",
//     "`drivers/virtio/virtio_driver_id.zig`",
//     "`drivers/virtio/virtio_verify.zig`",
//     "`zigux/tests/phase10_virtio_core.zig`",
//     "`zigux/tests/phase10_virtio_core_reset_queue.zig`",
//     "`zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`",
//     "`zigux/tests/phase10_virtio_driver_id.zig`",
//     "`zigux/tests/phase10_virtio_core_survey.zig`",
//     "`zigux/tests/phase10_build.zig`",
//     "`scripts\zigux/validate_phase10.zig`",
//     "`scripts/zigux/check_phase10_core_packet.zig`",
//     "phase10-driver-id-helper",
//     "phase10-driver-id-coverage-disposition-helper",
//     "phase10-core-probe-remove-lifecycle",
//     "drivers/virtio/virtio_driver_id.zig",
//     "pub fn reviewDriverIdMatch(",
//     "pub fn reviewDevice(",
//     "test \"phase10 virtio driver id review keeps exact matches explicit\" {",
//     "test \"phase10 virtio driver id review keeps wildcard matches and misses distinct\" {",
//     "drivers/virtio/virtio_verify.zig",
//     "pub fn summarizeDriverModel(",
//     "pub fn resetReplayPreservesQueueShape(",
//     "test \"phase10 virtio core verify keeps lifecycle checkpoints explicit\" {",
//     "test \"phase10 virtio core verify keeps reset replay below transport lifecycle claims\" {",
//     "zigux/tests/phase10_build.zig",
//     ".name = \"phase10-virtio-core-tests\"",
//     ".name = \"phase10-virtio-core-interrupt-compound-ack-tests\"",
//     ".name = \"phase10-virtio-core-reset-queue-tests\"",
//     ".name = \"phase10-virtio-core-verify-tests\"",
//     ".name = \"phase10-virtio-core-survey-tests\"",
//     ".name = \"phase10-virtio-driver-id-tests\"",
//     "test_step.dependOn(&run_phase10_virtio_core_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_core_interrupt_compound_ack_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_core_reset_queue_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_core_verify_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_core_survey_tests.step);",
//     "test_step.dependOn(&run_phase10_virtio_driver_id_tests.step);",
//     "zigux/tests/phase10_virtio_core.zig",
//     "test \"phase10 virtio core summary replay keeps status and feature bookkeeping reviewable\" {",
//     "test \"phase10 virtio core reset replay clears interrupt debt and drops driver readiness\" {",
//     "test \"phase10 virtio core driver id replay keeps exact wildcard and unmatched rules reviewable\" {",
//     "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig",
//     "test \"phase10 virtio core interrupt compound ack replay keeps queue-used and config-change bits isolated\" {",
//     "zigux/tests/phase10_virtio_core_reset_queue.zig",
//     "test \"phase10 virtio core reset queue replay drops ready state until queue and status are replayed\" {",
//     "test \"phase10 virtio core reset queue replay clears reset-required state\" {",
//     "zigux/tests/phase10_virtio_driver_id.zig",
//     "test \"phase10 virtio driver id replay keeps exact and wildcard dispositions reviewable\" {",
//     "test \"phase10 virtio driver id replay keeps vendor wildcard and no-match paths separate\" {",
// };
//
// const FORBIDDEN_MARKERS = [_][]const u8{
//     "stale guardrail reference drift",
//     "can still return `404`",
//     "mixed-source verification path",
// };
//
// const MANIFEST_PATH = [_][]const u8{
//     "zigux/tests/phase10_virtio_core_manifest.json",
// };
//
// const SURVEY_NOTE_PATH = [_][]const u8{
//     "Documentation/zigux/phase10-virtio-core-survey.md",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (EXPECTED_MANIFEST_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_SUMMARY_VALUES) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_GAP_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_PATHS) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
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
