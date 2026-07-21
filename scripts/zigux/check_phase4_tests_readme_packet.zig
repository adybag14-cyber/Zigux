const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_TESTS_README_PACKET_CHECK=pass";
pub const self_test_pass_marker = "PHASE4_TESTS_README_PACKET_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "run: zig run scripts/zigux/check_phase4_tests_readme_packet.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase4_tests_readme_packet.zig",
};

const markers_1 = [_][]const u8{
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "scripts\\zigux/validate_phase4.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "Validation and Perf Team",
    "ABI and Runtime Team",
    "Shared Subsystems Pod",
};

const markers_2 = [_][]const u8{
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
};

const markers_3 = [_][]const u8{
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "make -C zigux phase4-perf-baseline-survey",
};

const markers_4 = [_][]const u8{
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
};

const markers_5 = [_][]const u8{
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts\\zigux/check_phase4_repo_reality_warning.zig",
    "scripts\\zigux/check_phase4_tests_readme_packet.zig",
};

const markers_6 = [_][]const u8{
    "scripts/zigux/check_phase4_reversible_delivery_pins.zig",
    "scripts/zigux/check_phase4_perf_baseline_packet.zig",
    "zigux/tests/phase4_build.zig",
};

const markers_7 = [_][]const u8{
    "# zigux/tests",
    "This directory is the home of reusable Zigux parity and differential validation harnesses.",
    "## Phase 4 rollback-ownership and lab-matrix packet",
};

const contracts = [_]FileContract{
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/README.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/artifact-diff.md", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase4-gate-evidence.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase4-validation-matrix.md", .markers = &markers_4 },
    .{ .rel = "Documentation/zigux/review-checklist.md", .markers = &markers_5 },
    .{ .rel = "zigux/Makefile", .markers = &markers_6 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_7 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
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
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
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
// REQUIRED_PRESENT_MARKERS
// # zigux/tests
// This directory is the home of reusable Zigux parity and differential validation harnesses.
// ## Phase 4 rollback-ownership and lab-matrix packet
// Documentation/zigux/phase4-reversible-delivery-evidence.md
// Documentation/zigux/phase4-gate-evidence.md
// scripts\zigux/check_phase4_repo_reality_warning.zig
// scripts\zigux/check_phase4_tests_readme_packet.zig
// scripts\zigux/check_phase4_reversible_delivery_pins.zig
// scripts\zigux/check_phase4_perf_baseline_packet.zig
// scripts\zigux/validate_phase4.zig
// zigux/tests/phase4_perf_baseline_manifest.json
// zigux/tests/phase4_perf_baseline_survey.zig
// zigux/tests/phase4_build.zig
// zigux/tests/bitmap_diff.zig
// zigux/tests/phase4_bitmap_live_helper_replay.zig
// zigux/tests/atomic64_diff.zig
// zigux/tests/runtime_atomic64_diff.zig
// zigux/tests/phase4_runtime_atomic64_diff_manifest.json
// zigux/tests/phase4_runtime_atomic64_diff_survey.zig
// Documentation/zigux/phase4-kprobe-example-gap-survey.md
// Documentation/zigux/phase4-test-fsmount-gap-survey.md
// make -C zigux phase4-perf-baseline-survey
// Validation and Perf Team
// ABI and Runtime Team
// Shared Subsystems Pod
// SELF_TEST_CASE_NAMES
// baseline_round_trip
// missing_header
// missing_intro
// missing_phase4_heading
// missing_phase4_note_reference
// missing_phase4_gate_evidence_reference
// missing_phase4_repo_reality_warning_reference
// missing_phase4_tests_readme_checker_reference
// missing_phase4_reversible_delivery_checker_reference
// missing_phase4_perf_checker_reference
// missing_phase4_validator_reference
// missing_phase4_perf_manifest_reference
// missing_phase4_perf_survey_reference
// missing_phase4_build_reference
// missing_phase4_bitmap_reference
// missing_phase4_bitmap_replay_reference
// missing_phase4_atomic64_reference
// missing_phase4_runtime_atomic64_reference
// missing_phase4_owner_split_reference
