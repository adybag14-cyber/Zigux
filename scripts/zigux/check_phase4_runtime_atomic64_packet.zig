const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_RUNTIME_ATOMIC64_PACKET=pass";
pub const self_test_pass_marker = "PHASE4_RUNTIME_ATOMIC64_PACKET_SELF_TEST=pass";

const REQUIRED_REVERSIBLE_DELIVERY_MARKERS = [_][]const u8{
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_build.zig",
    "scripts\\zigux/validate_phase4.zig",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
};

const REQUIRED_SURVEY_MARKERS = [_][]const u8{
    "test \"phase 4 atomic64 survey keeps wrapper handoff, owner map, and current local-only perf evidence explicit\" {",
    "test \"phase 4 atomic64 survey keeps the current roadmap gap summary reviewable\" {",
    "test \"phase 4 atomic64 survey keeps reversible delivery and next-step evidence explicit\" {",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase4-validation-matrix.md",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
};

const REQUIRED_GATE_EVIDENCE_MARKERS = [_][]const u8{
    "PHASE4_VALIDATOR_BLOB_SHA=",
    "PHASE4_BUILD_BLOB_SHA=",
    "PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_BLOB_SHA=",
    "PHASE4_RUNTIME_ATOMIC64_SURVEY_PACKET_PRESENT=true",
    "PHASE4_SHARED_VALIDATOR_RERUNS_GATE_EVIDENCE_CHECK=true",
    "shared CI perf thresholds for the shipped atomic64 and bitmap rollback gates remain intentionally unapproved.",
};

const REQUIRED_PHASE4_MATRIX_MARKERS = [_][]const u8{
    "`zigux/tests/atomic64_diff.zig` bounded atomic64 exchange, cmpxchg, add_unless, bitwise, and selftest-family replay via the shared runtime-backed gate",
    "`zigux/tests/phase4_runtime_atomic64_diff_survey.zig` manifest-backed survey that keeps the wrapper, runtime replay body, validator, matrix, and reviewer checklist aligned around the same bounded atomic64 handoff",
    "`zig build phase4-runtime-atomic64-diff-survey --build-file zigux/tests/phase4_build.zig`",
    "`threshold_pending_until_runtime_atomic64_scope_widens`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
};

const REQUIRED_VALIDATOR_MARKERS = [_][]const u8{
    "phase4_runtime_atomic64_diff_manifest.json",
    "phase4_runtime_atomic64_diff_survey.zig",
    "run_phase4_runtime_atomic64_packet_check",
};

const REQUIRED_BUILD_MARKERS = [_][]const u8{
    "\"phase4-runtime-atomic64-diff\"",
    "\"phase4-runtime-atomic64-diff-survey\"",
    "runtime_atomic64_diff_step.dependOn(&run_atomic64_diff_tests.step);",
    "runtime_atomic64_diff_survey_step.dependOn(&run_runtime_atomic64_diff_survey_tests.step);",
};

const SELF_TEST_CASES = [_][]const u8{
    "baseline_round_trip",
    "missing_manifest_sha_field",
    "manifest_sha_drift",
    "missing_reversible_delivery_evidence",
    "reversible_delivery_marker_drift",
    "survey_marker_drift",
    "survey_sha_exact_count_drift",
    "gate_evidence_presence_flag_drift",
    "matrix_runtime_atomic64_marker_drift",
    "validator_runtime_atomic64_marker_drift",
    "build_runtime_atomic64_survey_route_drift",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_reversible_delivery_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_required_reversible_delivery_markers_path);
    const text_required_reversible_delivery_markers = try guard.readUtf8File(io, allocator, text_required_reversible_delivery_markers_path);
    defer allocator.free(text_required_reversible_delivery_markers);
    for (REQUIRED_REVERSIBLE_DELIVERY_MARKERS) |marker| try guard.requireMarker(text_required_reversible_delivery_markers, marker);
    const text_required_survey_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_required_survey_markers_path);
    const text_required_survey_markers = try guard.readUtf8File(io, allocator, text_required_survey_markers_path);
    defer allocator.free(text_required_survey_markers);
    for (REQUIRED_SURVEY_MARKERS) |marker| try guard.requireMarker(text_required_survey_markers, marker);
    const text_required_gate_evidence_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_required_gate_evidence_markers_path);
    const text_required_gate_evidence_markers = try guard.readUtf8File(io, allocator, text_required_gate_evidence_markers_path);
    defer allocator.free(text_required_gate_evidence_markers);
    for (REQUIRED_GATE_EVIDENCE_MARKERS) |marker| try guard.requireMarker(text_required_gate_evidence_markers, marker);
    const text_required_phase4_matrix_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_required_phase4_matrix_markers_path);
    const text_required_phase4_matrix_markers = try guard.readUtf8File(io, allocator, text_required_phase4_matrix_markers_path);
    defer allocator.free(text_required_phase4_matrix_markers);
    for (REQUIRED_PHASE4_MATRIX_MARKERS) |marker| try guard.requireMarker(text_required_phase4_matrix_markers, marker);
    const text_required_validator_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_required_validator_markers_path);
    const text_required_validator_markers = try guard.readUtf8File(io, allocator, text_required_validator_markers_path);
    defer allocator.free(text_required_validator_markers);
    for (REQUIRED_VALIDATOR_MARKERS) |marker| try guard.requireMarker(text_required_validator_markers, marker);
    const text_required_build_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_required_build_markers_path);
    const text_required_build_markers = try guard.readUtf8File(io, allocator, text_required_build_markers_path);
    defer allocator.free(text_required_build_markers);
    for (REQUIRED_BUILD_MARKERS) |marker| try guard.requireMarker(text_required_build_markers, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-gate-evidence.md");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
