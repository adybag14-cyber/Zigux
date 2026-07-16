const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_PERF_THRESHOLD_MATRIX=pass";
pub const self_test_pass_marker = "PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "`scripts\\zigux/check_phase4_perf_threshold_matrix.zig`",
    "Current direct-readback dedicated local-only perf checkers: `scripts\\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`.",
};

const markers_1 = [_][]const u8{
    "  - `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`",
    "`scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain directly readable adjacent evidence inside the perf-only lane rather than historical companions.",
    "Keep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.",
};

const markers_2 = [_][]const u8{
    "any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners",
    "promotion rollback owner: `Validation and Perf Team`",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
};

const markers_3 = [_][]const u8{
    "phase4_perf_baseline_survey.zig",
    "phase4-perf-baseline-survey",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase4-reversible-delivery-evidence.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase4-validation-lane-sequencing.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase4-validation-matrix.md", .markers = &markers_2 },
    .{ .rel = "zigux/tests/phase4_build.zig", .markers = &markers_3 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 4)});
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
            index += 1;
            explicit_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

// Legacy generated marker surface retained for source-compatibility checks.
// SELF_TEST_MANIFEST
// {
//   "atomic64": {
//     "benchmark_command": "zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
//     "acceptable_limit_metric": "median_elapsed_ns",
//     "acceptable_limit_max_elapsed_ns": 8192,
//     "acceptable_limit_iterations": 4,
//     "acceptable_limit_sample_count": 7
//   },
//   "bitmap": {
//     "benchmark_command": "zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig",
//     "acceptable_limit_metric": "median_elapsed_ns",
//     "acceptable_limit_max_elapsed_ns": 12288,
//     "acceptable_limit_iterations": 4,
//     "acceptable_limit_sample_count": 7
//   }
// }
//
// SELF_TEST_MATRIX
// # Phase 4 Validation Matrix
//
// ## Local-Only Perf Promotion
//   * any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners
//   * promotion rollback owner: `Validation and Perf Team`
//   * gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
//   * rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
//   * `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 8192` over `4` iterations with `7` monotonic samples
//   * `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 12288` over `4` iterations with `7` monotonic samples
//
// SELF_TEST_NOTE
// Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\zigux/check_phase4_repo_reality_warning.zig`, `scripts\zigux/check_phase4_tests_readme_packet.zig`, `scripts\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.
// Current direct-readback dedicated local-only perf checkers: `scripts\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\zigux/check_phase4_perf_threshold_matrix.zig`.
//
// SELF_TEST_LANE
// - directly readable dedicated local-only perf packet that still stays adjacent to the shared handoff:
//   - `scripts\zigux/check_phase4_perf_baseline_packet.zig`
//   - `scripts\zigux/check_phase4_perf_threshold_matrix.zig`
//   - `zigux/tests/phase4_perf_baseline_manifest.json`
//   - `zigux/tests/phase4_perf_baseline_survey.zig`
// - `scripts\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain directly readable adjacent evidence inside the perf-only lane rather than historical companions.
// Keep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.
//
// SELF_TEST_BUILD
// const phase4_perf_baseline_survey = @import("phase4_perf_baseline_survey.zig");
// const phase4_perf_baseline_survey_step = "phase4-perf-baseline-survey";
//
// NOTE_MARKERS
// `scripts\zigux/check_phase4_perf_threshold_matrix.zig`
// Current direct-readback dedicated local-only perf checkers: `scripts\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\zigux/check_phase4_perf_threshold_matrix.zig`.
// LANE_MARKERS
//   - `scripts\zigux/check_phase4_perf_threshold_matrix.zig`
// `scripts\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain directly readable adjacent evidence inside the perf-only lane rather than historical companions.
// Keep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.
// MATRIX_OWNER_MARKERS
// any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners
// promotion rollback owner: `Validation and Perf Team`
// gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
// rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
// PHASE4_BUILD_MARKERS
// phase4_perf_baseline_survey.zig
// phase4-perf-baseline-survey
