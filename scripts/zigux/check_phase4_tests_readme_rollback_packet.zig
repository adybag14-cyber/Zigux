const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE4_TESTS_README_ROLLBACK_PACKET=pass";
pub const self_test_pass_marker = "CHECK_PHASE4_TESTS_README_ROLLBACK_PACKET_SELF_TEST=pass";

const PASS_MARKER = [_][]const u8{
    "PHASE4_TESTS_README_ROLLBACK_PACKET_CHECK=pass",
};

const SELF_TEST_PASS_MARKER = [_][]const u8{
    "PHASE4_TESTS_README_ROLLBACK_PACKET_SELF_TEST=pass",
};

const REQUIRED_README_MARKERS = [_][]const u8{
    "current direct-readback Phase 4 rollback packet:",
    "direct readback now confirms the broader current Phase 4 validator, lab-matrix, and local-only perf companions on current `master`, including `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/validate_phase4.zig`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig`",
    "Phase 4 follow-through should treat the stale part of that handoff as historical blob-pin provenance in `Documentation/zigux/phase4-reversible-delivery-evidence.md`, not as path absence on current `master`",
    "the parked kprobe and `test_fsmount` survey companions stay adjacent but separate while those current validator, lab-matrix, and local-only perf companions remain directly readable on current `master`",
};

const FORBIDDEN_README_MARKERS = [_][]const u8{
    "return missing contents reads on current `master`",
    "require fresh reread or re-materialization before they are presented as shipped direct evidence again",
    "until a fresh reread confirms they are directly readable again on current `master`",
};

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/validate_phase4.zig`, `zigux/tests/phase4_build.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "The tests-root guide should mirror this same current-head posture.",
    "stop describing those present Phase 4 validator, lab-matrix, and local-only perf companions as missing on current `master`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_pass_marker_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_pass_marker_path);
    const text_pass_marker = try guard.readUtf8File(io, allocator, text_pass_marker_path);
    defer allocator.free(text_pass_marker);
    for (PASS_MARKER) |marker| try guard.requireMarker(text_pass_marker, marker);
    const text_self_test_pass_marker_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_self_test_pass_marker_path);
    const text_self_test_pass_marker = try guard.readUtf8File(io, allocator, text_self_test_pass_marker_path);
    defer allocator.free(text_self_test_pass_marker);
    for (SELF_TEST_PASS_MARKER) |marker| try guard.requireMarker(text_self_test_pass_marker, marker);
    const text_required_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_required_readme_markers_path);
    const text_required_readme_markers = try guard.readUtf8File(io, allocator, text_required_readme_markers_path);
    defer allocator.free(text_required_readme_markers);
    for (REQUIRED_README_MARKERS) |marker| try guard.requireMarker(text_required_readme_markers, marker);
    const text_forbidden_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_forbidden_readme_markers_path);
    const text_forbidden_readme_markers = try guard.readUtf8File(io, allocator, text_forbidden_readme_markers_path);
    defer allocator.free(text_forbidden_readme_markers);
    for (FORBIDDEN_README_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_readme_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_required_note_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_required_note_markers_path);
    const text_required_note_markers = try guard.readUtf8File(io, allocator, text_required_note_markers_path);
    defer allocator.free(text_required_note_markers);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_required_note_markers, marker);
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
