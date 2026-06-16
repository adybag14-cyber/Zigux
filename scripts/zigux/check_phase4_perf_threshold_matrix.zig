const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_PERF_THRESHOLD_MATRIX=pass";
pub const self_test_pass_marker = "PHASE4_PERF_THRESHOLD_MATRIX_SELF_TEST=pass";

const SELF_TEST_MANIFEST = [_][]const u8{
    "{\n  \"atomic64\": {\n    \"benchmark_command\": \"zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig\",\n    \"acceptable_limit_metric\": \"median_elapsed_ns\",\n    \"acceptable_limit_max_elapsed_ns\": 8192,\n    \"acceptable_limit_iterations\": 4,\n    \"acceptable_limit_sample_count\": 7\n  },\n  \"bitmap\": {\n    \"benchmark_command\": \"zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig\",\n    \"acceptable_limit_metric\": \"median_elapsed_ns\",\n    \"acceptable_limit_max_elapsed_ns\": 12288,\n    \"acceptable_limit_iterations\": 4,\n    \"acceptable_limit_sample_count\": 7\n  }\n}\n",
};

const SELF_TEST_MATRIX = [_][]const u8{
    "# Phase 4 Validation Matrix\n\n## Local-Only Perf Promotion\n  * any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners\n  * promotion rollback owner: `Validation and Perf Team`\n  * gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`\n  * rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`\n  * `zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 8192` over `4` iterations with `7` monotonic samples\n  * `zig build phase4-bitmap-diff --build-file zigux/tests/phase4_build.zig` approved local-only acceptable limit: `median_elapsed_ns <= 12288` over `4` iterations with `7` monotonic samples\n",
};

const SELF_TEST_NOTE = [_][]const u8{
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_tests_readme_packet.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.\nCurrent direct-readback dedicated local-only perf checkers: `scripts\\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`.\n",
};

const SELF_TEST_LANE = [_][]const u8{
    "- directly readable dedicated local-only perf packet that still stays adjacent to the shared handoff:\n  - `scripts\\zigux/check_phase4_perf_baseline_packet.zig`\n  - `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`\n  - `zigux/tests/phase4_perf_baseline_manifest.json`\n  - `zigux/tests/phase4_perf_baseline_survey.zig`\n- `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain directly readable adjacent evidence inside the perf-only lane rather than historical companions.\nKeep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.\n",
};

const SELF_TEST_BUILD = [_][]const u8{
    "const phase4_perf_baseline_survey = @import(\"phase4_perf_baseline_survey.zig\");\nconst phase4_perf_baseline_survey_step = \"phase4-perf-baseline-survey\";\n",
};

const NOTE_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase4_perf_threshold_matrix.zig`",
    "Current direct-readback dedicated local-only perf checkers: `scripts\\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`.",
};

const LANE_MARKERS = [_][]const u8{
    "  - `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`",
    "`scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` remain directly readable adjacent evidence inside the perf-only lane rather than historical companions.",
    "Keep the Validation and Perf Team decision-owner and rollback-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.",
};

const MATRIX_OWNER_MARKERS = [_][]const u8{
    "any future shared CI perf-promotion claim must name the Validation and Perf Team as the decision owner and rollback owner, and the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners",
    "promotion rollback owner: `Validation and Perf Team`",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
};

const PHASE4_BUILD_MARKERS = [_][]const u8{
    "phase4_perf_baseline_survey.zig",
    "phase4-perf-baseline-survey",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_self_test_manifest_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_self_test_manifest_path);
    const text_self_test_manifest = try guard.readUtf8File(io, allocator, text_self_test_manifest_path);
    defer allocator.free(text_self_test_manifest);
    for (SELF_TEST_MANIFEST) |marker| try guard.requireMarker(text_self_test_manifest, marker);
    const text_self_test_matrix_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_self_test_matrix_path);
    const text_self_test_matrix = try guard.readUtf8File(io, allocator, text_self_test_matrix_path);
    defer allocator.free(text_self_test_matrix);
    for (SELF_TEST_MATRIX) |marker| try guard.requireMarker(text_self_test_matrix, marker);
    const text_self_test_note_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_self_test_note_path);
    const text_self_test_note = try guard.readUtf8File(io, allocator, text_self_test_note_path);
    defer allocator.free(text_self_test_note);
    for (SELF_TEST_NOTE) |marker| try guard.requireMarker(text_self_test_note, marker);
    const text_self_test_lane_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_self_test_lane_path);
    const text_self_test_lane = try guard.readUtf8File(io, allocator, text_self_test_lane_path);
    defer allocator.free(text_self_test_lane);
    for (SELF_TEST_LANE) |marker| try guard.requireMarker(text_self_test_lane, marker);
    const text_self_test_build_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_self_test_build_path);
    const text_self_test_build = try guard.readUtf8File(io, allocator, text_self_test_build_path);
    defer allocator.free(text_self_test_build);
    for (SELF_TEST_BUILD) |marker| try guard.requireMarker(text_self_test_build, marker);
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-reversible-delivery-evidence.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
    const text_lane_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-lane-sequencing.md");
    defer allocator.free(text_lane_markers_path);
    const text_lane_markers = try guard.readUtf8File(io, allocator, text_lane_markers_path);
    defer allocator.free(text_lane_markers);
    for (LANE_MARKERS) |marker| try guard.requireMarker(text_lane_markers, marker);
    const text_matrix_owner_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_matrix_owner_markers_path);
    const text_matrix_owner_markers = try guard.readUtf8File(io, allocator, text_matrix_owner_markers_path);
    defer allocator.free(text_matrix_owner_markers);
    for (MATRIX_OWNER_MARKERS) |marker| try guard.requireMarker(text_matrix_owner_markers, marker);
    const text_phase4_build_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase4_build.zig");
    defer allocator.free(text_phase4_build_markers_path);
    const text_phase4_build_markers = try guard.readUtf8File(io, allocator, text_phase4_build_markers_path);
    defer allocator.free(text_phase4_build_markers);
    for (PHASE4_BUILD_MARKERS) |marker| try guard.requireMarker(text_phase4_build_markers, marker);
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
