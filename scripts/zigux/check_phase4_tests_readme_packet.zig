const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_TESTS_README_PACKET_CHECK=pass";
pub const self_test_pass_marker = "PHASE4_TESTS_README_PACKET_SELF_TEST=pass";

const REQUIRED_PRESENT_MARKERS = [_][]const u8{
    "# zigux/tests",
    "This directory is the home of reusable Zigux parity and differential validation harnesses.",
    "## Phase 4 rollback-ownership and lab-matrix packet",
    "Documentation/zigux/phase4-reversible-delivery-evidence.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "scripts\\zigux/check_phase4_repo_reality_warning.zig",
    "scripts\\zigux/check_phase4_tests_readme_packet.zig",
    "scripts\\zigux/check_phase4_reversible_delivery_pins.zig",
    "scripts\\zigux/check_phase4_perf_baseline_packet.zig",
    "scripts\\zigux/validate_phase4.zig",
    "zigux/tests/phase4_perf_baseline_manifest.json",
    "zigux/tests/phase4_perf_baseline_survey.zig",
    "zigux/tests/phase4_build.zig",
    "zigux/tests/bitmap_diff.zig",
    "zigux/tests/phase4_bitmap_live_helper_replay.zig",
    "zigux/tests/atomic64_diff.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase4_runtime_atomic64_diff_manifest.json",
    "zigux/tests/phase4_runtime_atomic64_diff_survey.zig",
    "Documentation/zigux/phase4-kprobe-example-gap-survey.md",
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "make -C zigux phase4-perf-baseline-survey",
    "Validation and Perf Team",
    "ABI and Runtime Team",
    "Shared Subsystems Pod",
};

const SELF_TEST_CASE_NAMES = [_][]const u8{
    "baseline_round_trip",
    "missing_header",
    "missing_intro",
    "missing_phase4_heading",
    "missing_phase4_note_reference",
    "missing_phase4_gate_evidence_reference",
    "missing_phase4_repo_reality_warning_reference",
    "missing_phase4_tests_readme_checker_reference",
    "missing_phase4_reversible_delivery_checker_reference",
    "missing_phase4_perf_checker_reference",
    "missing_phase4_validator_reference",
    "missing_phase4_perf_manifest_reference",
    "missing_phase4_perf_survey_reference",
    "missing_phase4_build_reference",
    "missing_phase4_bitmap_reference",
    "missing_phase4_bitmap_replay_reference",
    "missing_phase4_atomic64_reference",
    "missing_phase4_runtime_atomic64_reference",
    "missing_phase4_owner_split_reference",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_present_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_required_present_markers_path);
    const text_required_present_markers = try guard.readUtf8File(io, allocator, text_required_present_markers_path);
    defer allocator.free(text_required_present_markers);
    for (REQUIRED_PRESENT_MARKERS) |marker| try guard.requireMarker(text_required_present_markers, marker);
    const text_self_test_case_names_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_case_names_path);
    const text_self_test_case_names = try guard.readUtf8File(io, allocator, text_self_test_case_names_path);
    defer allocator.free(text_self_test_case_names);
    for (SELF_TEST_CASE_NAMES) |marker| try guard.requireMarker(text_self_test_case_names, marker);
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
