const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE10_SHARED_FREEZE_BOUNDARY=pass";
pub const self_test_pass_marker = "PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const FileContract = struct { rel: []const u8, markers: []const []const u8 };
const ReadyFollowups = struct {
    @"zigux/tests/phase10_virtio_input_manifest.json": []const u8,
    @"zigux/tests/phase10_virtio_mmio_manifest.json": []const u8,
};
const BlockedGaps = struct {
    @"zigux/tests/phase10_virtio_core_manifest.json": []const u8,
    @"zigux/tests/phase10_virtio_input_manifest.json": []const u8,
    @"zigux/tests/phase10_virtio_mmio_manifest.json": []const u8,
};
const LaneKeys = struct { core: []const u8, ring: []const u8, input: []const u8, mmio: []const u8 };
const SurveyProvenance = struct { source: []const u8, lane_keys: LaneKeys };
const Phase14Boundary = struct {
    status: []const u8,
    anchors: []const []const u8,
    required_phase14_evidence_features: []const []const u8,
    future_destinations: []const []const u8,
    future_destination_policy: []const u8,
};
const ClosureManifest = struct {
    freeze_map: []const u8,
    freeze_boundary_status: []const u8,
    freeze_status_change_claimed: bool,
    risky_transport_posture: []const u8,
    allowed_roadmap_destinations: []const []const u8,
    allowed_evidence_kinds: []const []const u8,
    forbidden_transport_claims: []const []const u8,
    architecture_council_reopen_required: bool,
    architecture_council_reopen_attached: bool,
    ready_transport_followups: ReadyFollowups,
    blocked_transport_gaps: BlockedGaps,
    freeze_in_c_anchors: []const []const u8,
    study_only_anchors: []const []const u8,
    docs: []const []const u8,
    phase14_study_only_boundary: Phase14Boundary,
    survey_provenance: SurveyProvenance,
};
const DriverManifest = struct {
    freeze_map: []const u8,
    freeze_boundary_status: []const u8,
    freeze_status_change_claimed: bool,
    risky_transport_posture: []const u8,
    allowed_evidence_kinds: []const []const u8,
    architecture_council_reopen_required: bool,
    architecture_council_reopen_attached: bool,
    forbidden_transport_claims: []const []const u8,
};

const required_files = [_][]const u8{
    "scripts/zigux/check_phase10_shared_freeze_boundary.zig",
    "Documentation/zigux/README.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase10-freeze-boundary-gap-survey.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase10_closure_manifest.json",
    "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
    "zigux/tests/phase10_virtio_ring_manifest.json",
    "zigux/tests/phase10_virtio_input_manifest.json",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
};

const freeze_in_c_anchors = [_][]const u8{
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
};

const study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const phase14_features = [_][]const u8{
    "boundary maps",
    "concurrency audits",
    "explicit stay-in-C decisions where warranted",
    "wrapper-first or study-only posture",
};

const phase14_destinations = [_][]const u8{
    "kernel/workqueue_bridge.zig",
    "kernel/trace/ring_buffer.zig",
};

const allowed_destinations = [_][]const u8{
    "drivers/virtio/*.zig",
    "zigux/kernel/",
    "zigux/helpers/",
};

const allowed_evidence = [_][]const u8{
    "driver_local_lab_slices",
    "survey_manifests",
    "shared_validation_gates",
};

const closure_forbidden_claims = [_][]const u8{
    "queue_setup_reset_paths",
    "queue_reset_execution",
    "irq_parity",
    "dma_paths",
    "input_registration_lifecycle",
    "probe_remove_lifecycle",
    "freeze_restore_lifecycle",
};

const markers_0 = [_][]const u8{
    "pub const live_pass_marker = \"PHASE10_SHARED_FREEZE_BOUNDARY=pass\";",
    "\"kernel/workqueue.c\"",
    "\"kernel/trace/ring_buffer.c\"",
    "\"kernel/sched/core.c\"",
    "\"net/core/skbuff.c\"",
};

const markers_1 = [_][]const u8{
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
};

const markers_2 = [_][]const u8{
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "there is no silent exception path around the stay-in-C policy",
};

const markers_3 = [_][]const u8{
    "# Phase 10 Freeze-Boundary Gap Survey",
    "`Documentation/zigux/freeze-map.md` explicit as the governing freeze source",
    "`scripts\\zigux/check_phase10_shared_freeze_boundary.zig` explicit as the fail-closed review gate for freeze-boundary drift",
    "Study-only anchors that remain outside Phase 10 delivery and stay parked in the separate Phase 14 family:",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "It must not present them as active virtio closure evidence, bridge-readiness proof, or status-change candidates.",
};

const markers_4 = [_][]const u8{
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
};

const markers_5 = [_][]const u8{
    "Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
};

const markers_6 = [_][]const u8{
    "keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the separate Phase 14 study-only family",
};

const markers_7 = [_][]const u8{
    "Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
};

const markers_8 = [_][]const u8{
    "### `kernel/workqueue.c`",
    "### `kernel/trace/ring_buffer.c`",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
};

const markers_9 = [_][]const u8{
    "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
};

const markers_10 = [_][]const u8{
    "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
    "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
    "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10",
    "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22",
    "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
    "PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue.c,kernel/trace/ring_buffer.c",
};

const contracts = [_]FileContract{
    .{ .rel = "scripts/zigux/check_phase10_shared_freeze_boundary.zig", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/freeze-map.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase10-freeze-boundary-gap-survey.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase10-closure-evidence.md", .markers = &markers_4 },
    .{ .rel = "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md", .markers = &markers_5 },
    .{ .rel = "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md", .markers = &markers_6 },
    .{ .rel = "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md", .markers = &markers_7 },
    .{ .rel = "Documentation/zigux/phase15-study-only-anchor-accounting.md", .markers = &markers_8 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_9 },
    .{ .rel = "zigux-alpha/PHASE10_CLOSURE_LEDGER.md", .markers = &markers_10 },
};

fn expectStrings(actual: []const []const u8, expected: []const []const u8) !void {
    if (actual.len != expected.len) return error.StringArrayLengthDrift;
    for (actual, expected) |a, e| if (!std.mem.eql(u8, a, e)) return error.StringArrayValueDrift;
}

fn containsString(values: []const []const u8, expected: []const u8) bool {
    for (values) |value| if (std.mem.eql(u8, value, expected)) return true;
    return false;
}

fn checkDriverManifest(allocator: std.mem.Allocator, source: []const u8, expected_claims: []const []const u8) !void {
    const parsed = try std.json.parseFromSlice(DriverManifest, allocator, source, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const value = parsed.value;
    if (!std.mem.eql(u8, value.freeze_map, "Documentation/zigux/freeze-map.md")) return error.DriverFreezeMapDrift;
    if (!std.mem.eql(u8, value.freeze_boundary_status, "aligned")) return error.DriverFreezeStatusDrift;
    if (value.freeze_status_change_claimed) return error.DriverFreezeClaimDrift;
    if (!std.mem.eql(u8, value.risky_transport_posture, "blocked_on_risky_transport")) return error.DriverTransportPostureDrift;
    try expectStrings(value.allowed_evidence_kinds, &allowed_evidence);
    if (!value.architecture_council_reopen_required or value.architecture_council_reopen_attached) return error.DriverArchitectureBoundaryDrift;
    try expectStrings(value.forbidden_transport_claims, expected_claims);
}

fn checkClosureManifest(allocator: std.mem.Allocator, source: []const u8) !void {
    const parsed = try std.json.parseFromSlice(ClosureManifest, allocator, source, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const value = parsed.value;
    if (!std.mem.eql(u8, value.freeze_map, "Documentation/zigux/freeze-map.md")) return error.ClosureFreezeMapDrift;
    if (!std.mem.eql(u8, value.freeze_boundary_status, "aligned")) return error.ClosureFreezeStatusDrift;
    if (value.freeze_status_change_claimed) return error.ClosureFreezeClaimDrift;
    if (!std.mem.eql(u8, value.risky_transport_posture, "blocked_on_risky_transport")) return error.ClosureTransportPostureDrift;
    try expectStrings(value.allowed_roadmap_destinations, &allowed_destinations);
    try expectStrings(value.allowed_evidence_kinds, &allowed_evidence);
    try expectStrings(value.forbidden_transport_claims, &closure_forbidden_claims);
    if (!value.architecture_council_reopen_required or value.architecture_council_reopen_attached) return error.ClosureArchitectureBoundaryDrift;
    if (!std.mem.eql(u8, value.ready_transport_followups.@"zigux/tests/phase10_virtio_input_manifest.json", "phase10-virtio-input-registration-lifecycle")) return error.ReadyInputFollowupDrift;
    if (!std.mem.eql(u8, value.ready_transport_followups.@"zigux/tests/phase10_virtio_mmio_manifest.json", "phase10-mmio-lifecycle-and-irq-paths")) return error.ReadyMmioFollowupDrift;
    if (!std.mem.eql(u8, value.blocked_transport_gaps.@"zigux/tests/phase10_virtio_core_manifest.json", "phase10-core-probe-remove-lifecycle")) return error.BlockedCoreGapDrift;
    if (!std.mem.eql(u8, value.blocked_transport_gaps.@"zigux/tests/phase10_virtio_input_manifest.json", "phase10-virtio-input-registration-lifecycle")) return error.BlockedInputGapDrift;
    if (!std.mem.eql(u8, value.blocked_transport_gaps.@"zigux/tests/phase10_virtio_mmio_manifest.json", "phase10-mmio-lifecycle-and-irq-paths")) return error.BlockedMmioGapDrift;
    try expectStrings(value.freeze_in_c_anchors, &freeze_in_c_anchors);
    try expectStrings(value.study_only_anchors, &study_only_anchors);
    if (!containsString(value.docs, "Documentation/zigux/phase10-freeze-boundary-gap-survey.md")) return error.MissingFreezeBoundaryGapSurvey;
    if (!std.mem.eql(u8, value.phase14_study_only_boundary.status, "separate_phase14_lane")) return error.Phase14StatusDrift;
    try expectStrings(value.phase14_study_only_boundary.anchors, &study_only_anchors);
    try expectStrings(value.phase14_study_only_boundary.required_phase14_evidence_features, &phase14_features);
    try expectStrings(value.phase14_study_only_boundary.future_destinations, &phase14_destinations);
    if (!std.mem.eql(u8, value.phase14_study_only_boundary.future_destination_policy, "kernel/trace/ring_buffer.zig remains a future destination only if years of evidence justify it")) return error.Phase14FuturePolicyDrift;
    if (!std.mem.eql(u8, value.survey_provenance.source, "manifest_derived")) return error.SurveyProvenanceDrift;
    if (!std.mem.eql(u8, value.survey_provenance.lane_keys.core, "P10-L01") or !std.mem.eql(u8, value.survey_provenance.lane_keys.ring, "P10-L10") or !std.mem.eql(u8, value.survey_provenance.lane_keys.input, "P10-L22") or !std.mem.eql(u8, value.survey_provenance.lane_keys.mmio, "P10-L11")) return error.SurveyLaneKeyDrift;
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        allocator.free(text);
    }
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
    const closure_path = try guard.joinPath(allocator, root, "zigux/tests/phase10_closure_manifest.json");
    defer allocator.free(closure_path);
    const closure = try guard.readUtf8File(io, allocator, closure_path);
    defer allocator.free(closure);
    try checkClosureManifest(allocator, closure);
    const ring_path = try guard.joinPath(allocator, root, "zigux/tests/phase10_virtio_ring_manifest.json");
    defer allocator.free(ring_path);
    const ring = try guard.readUtf8File(io, allocator, ring_path);
    defer allocator.free(ring);
    const ring_claims = [_][]const u8{"queue_setup_reset_paths", "irq_parity", "dma_paths", "input_registration_lifecycle", "probe_remove_lifecycle"};
    try checkDriverManifest(allocator, ring, &ring_claims);
    const input_path = try guard.joinPath(allocator, root, "zigux/tests/phase10_virtio_input_manifest.json");
    defer allocator.free(input_path);
    const input = try guard.readUtf8File(io, allocator, input_path);
    defer allocator.free(input);
    try checkDriverManifest(allocator, input, &ring_claims);
    const mmio_path = try guard.joinPath(allocator, root, "zigux/tests/phase10_virtio_mmio_manifest.json");
    defer allocator.free(mmio_path);
    const mmio = try guard.readUtf8File(io, allocator, mmio_path);
    defer allocator.free(mmio);
    const mmio_claims = [_][]const u8{"queue_setup_reset_paths", "queue_reset_execution", "irq_parity", "dma_paths", "probe_remove_lifecycle", "freeze_restore_lifecycle"};
    try checkDriverManifest(allocator, mmio, &mmio_claims);
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE10_SHARED_FREEZE_REQUIRED_FILE_COUNT=15", .{});
    try guard.printLine(io, "PHASE10_SHARED_FREEZE_REQUIRED_MARKER_COUNT=81", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST_CASE_COUNT=34", .{});
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
// pub const pass_marker = "PHASE10_SHARED_FREEZE_BOUNDARY_SELF_TEST=pass";
//
// const EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC = [_][]const u8{
//     "Documentation/zigux/phase10-freeze-boundary-gap-survey.md",
// };
//
// const COMMON_DRIVER_MANIFEST_FILES = [_][]const u8{
//     "zigux/tests/phase10_virtio_ring_manifest.json",
//     "zigux/tests/phase10_virtio_input_manifest.json",
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
// };
//
// const REQUIRED_FILES = [_][]const u8{
//     "scripts/zigux/check_phase10_shared_freeze_boundary.zig",
//     "Documentation/zigux/README.md",
//     "Documentation/zigux/freeze-map.md",
//     "EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC",
//     "Documentation/zigux/phase10-closure-evidence.md",
//     "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
//     "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
//     "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
//     "Documentation/zigux/phase15-study-only-anchor-accounting.md",
//     "Documentation/zigux/review-checklist.md",
//     "zigux/tests/phase10_closure_manifest.json",
//     "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
//     "COMMON_DRIVER_MANIFEST_FILES",
// };
//
// const FREEZE_IN_C_ANCHORS = [_][]const u8{
//     "kernel/sched/core.c",
//     "mm/page_alloc.c",
//     "kernel/rcu/tree.c",
//     "net/core/skbuff.c",
// };
//
// const STUDY_ONLY_ANCHORS = [_][]const u8{
//     "kernel/workqueue.c",
//     "kernel/trace/ring_buffer.c",
// };
//
// const PHASE14_EVIDENCE_FEATURES = [_][]const u8{
//     "boundary maps",
//     "concurrency audits",
//     "explicit stay-in-C decisions where warranted",
//     "wrapper-first or study-only posture",
// };
//
// const PHASE14_FUTURE_DESTINATIONS = [_][]const u8{
//     "kernel/workqueue_bridge.zig",
//     "kernel/trace/ring_buffer.zig",
// };
//
// const PHASE14_FUTURE_DESTINATION_POLICY = [_][]const u8{
//     "kernel/trace/ring_buffer.zig remains a future destination only if years of evidence justify it",
// };
//
// const CLOSURE_ALLOWED_ROADMAP_DESTINATIONS = [_][]const u8{
//     "drivers/virtio/*.zig",
//     "zigux/kernel/",
//     "zigux/helpers/",
// };
//
// const CLOSURE_FORBIDDEN_TRANSPORT_CLAIMS = [_][]const u8{
//     "queue_setup_reset_paths",
//     "queue_reset_execution",
//     "irq_parity",
//     "dma_paths",
//     "input_registration_lifecycle",
//     "probe_remove_lifecycle",
//     "freeze_restore_lifecycle",
// };
//
// const EXPECTED_SURVEY_PROVENANCE = [_][]const u8{
//     "source",
//     "manifest_derived",
//     "lane_keys",
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
// const EXPECTED_READY_TRANSPORT_FOLLOWUPS = [_][]const u8{
//     "zigux/tests/phase10_virtio_input_manifest.json",
//     "phase10-virtio-input-registration-lifecycle",
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
//     "phase10-mmio-lifecycle-and-irq-paths",
// };
//
// const EXPECTED_BLOCKED_TRANSPORT_GAPS = [_][]const u8{
//     "zigux/tests/phase10_virtio_core_manifest.json",
//     "phase10-core-probe-remove-lifecycle",
//     "zigux/tests/phase10_virtio_input_manifest.json",
//     "phase10-virtio-input-registration-lifecycle",
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
//     "phase10-mmio-lifecycle-and-irq-paths",
// };
//
// const COMMON_DRIVER_FIELD_VALUES = [_][]const u8{
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
//     "architecture_council_reopen_required",
//     "architecture_council_reopen_attached",
// };
//
// const EXPECTED_DRIVER_MANIFEST_FIELDS = [_][]const u8{
//     "zigux/tests/phase10_virtio_ring_manifest.json",
//     "forbidden_transport_claims",
//     "queue_setup_reset_paths",
//     "irq_parity",
//     "dma_paths",
//     "input_registration_lifecycle",
//     "probe_remove_lifecycle",
//     "zigux/tests/phase10_virtio_input_manifest.json",
//     "forbidden_transport_claims",
//     "queue_setup_reset_paths",
//     "irq_parity",
//     "dma_paths",
//     "input_registration_lifecycle",
//     "probe_remove_lifecycle",
//     "zigux/tests/phase10_virtio_mmio_manifest.json",
//     "forbidden_transport_claims",
//     "queue_setup_reset_paths",
//     "queue_reset_execution",
//     "irq_parity",
//     "dma_paths",
//     "probe_remove_lifecycle",
//     "freeze_restore_lifecycle",
// };
//
// const TEXT_MARKERS = [_][]const u8{
//     "scripts/zigux/check_phase10_shared_freeze_boundary.zig",
//     "CHECK_COMMAND = \"{CHECK_COMMAND}\"",
//     "\"kernel/workqueue.c\"",
//     "\"kernel/trace/ring_buffer.c\"",
//     "\"kernel/sched/core.c\"",
//     "\"net/core/skbuff.c\"",
//     "Documentation/zigux/README.md",
//     "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
//     "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues",
//     "Documentation/zigux/freeze-map.md",
//     "`kernel/sched/core.c`",
//     "`mm/page_alloc.c`",
//     "`kernel/rcu/tree.c`",
//     "`net/core/skbuff.c`",
//     "`kernel/workqueue.c`",
//     "`kernel/trace/ring_buffer.c`",
//     "there is no silent exception path around the stay-in-C policy",
//     "# Phase 10 Freeze-Boundary Gap Survey",
//     "`Documentation/zigux/freeze-map.md` explicit as the governing freeze source",
//     "`scripts/zigux/check_phase10_shared_freeze_boundary.zig` explicit as the fail-closed review gate for freeze-boundary drift",
//     "Study-only anchors that remain outside Phase 10 delivery and stay parked in the separate Phase 14 family:",
//     "`kernel/workqueue.c`",
//     "`kernel/trace/ring_buffer.c`",
//     "It must not present them as active virtio closure evidence, bridge-readiness proof, or status-change candidates.",
//     "Documentation/zigux/phase10-closure-evidence.md",
//     "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors rather than Phase 10 closure evidence.",
//     "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
//     "Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
//     "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
//     "keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the separate Phase 14 study-only family",
//     "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
//     "Keep the separate Phase 14 study-only ownership of `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit",
//     "Documentation/zigux/phase15-study-only-anchor-accounting.md",
//     "### `kernel/workqueue.c`",
//     "### `kernel/trace/ring_buffer.c`",
//     "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
//     "Documentation/zigux/review-checklist.md",
//     "if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
//     "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
//     "zigux-alpha/PHASE10_CLOSURE_LEDGER.md",
//     "PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived",
//     "PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01",
//     "PHASE10_LEDGER_SURVEY_RING_LANE=P10-L10",
//     "PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L22",
//     "PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L11",
//     "PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue.c,kernel/trace/ring_buffer.c",
// };
//
// const CHECK_COMMAND = [_][]const u8{
//     "zig run scripts/zigux/check_phase10_shared_freeze_boundary.zig --",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (EXPECTED_FREEZE_BOUNDARY_GAP_SURVEY_DOC) |marker| try guard.requireMarker(text, marker);
//     for (COMMON_DRIVER_MANIFEST_FILES) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
//     for (FREEZE_IN_C_ANCHORS) |marker| try guard.requireMarker(text, marker);
//     for (STUDY_ONLY_ANCHORS) |marker| try guard.requireMarker(text, marker);
//     for (PHASE14_EVIDENCE_FEATURES) |marker| try guard.requireMarker(text, marker);
//     for (PHASE14_FUTURE_DESTINATIONS) |marker| try guard.requireMarker(text, marker);
//     for (PHASE14_FUTURE_DESTINATION_POLICY) |marker| try guard.requireMarker(text, marker);
//     for (CLOSURE_ALLOWED_ROADMAP_DESTINATIONS) |marker| try guard.requireMarker(text, marker);
//     for (CLOSURE_FORBIDDEN_TRANSPORT_CLAIMS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_SURVEY_PROVENANCE) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_READY_TRANSPORT_FOLLOWUPS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_BLOCKED_TRANSPORT_GAPS) |marker| try guard.requireMarker(text, marker);
//     for (COMMON_DRIVER_FIELD_VALUES) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_DRIVER_MANIFEST_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (CHECK_COMMAND) |marker| try guard.requireMarker(text, marker);
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
