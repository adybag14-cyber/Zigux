const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_VALIDATION_LANE_SEQUENCING_CHECK=pass";
pub const self_test_pass_marker = "PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST=pass";

const SEQUENCING_MARKERS = [_][]const u8{
    "current direct-readback shared handoff:",
    "`scripts\\zigux/check_phase4_repo_reality_warning.zig`",
    "recovered broader shared exact-readback and owner-map companions that now reread directly on current `master`:",
    "`Documentation/zigux/phase4-validation-lane-sequencing.md`",
    "Current shared reminder ownership is narrower than that historical label: `P4-L24` now covers the matrix-side and sequencing-note reminder wording around `Documentation/zigux/phase4-validation-matrix.md` plus `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, while the live `P4-L19` lane now owns checker-local measurability follow-through",
    "If the drift is limited to the matrix-side or sequencing-note reminder surfaces around `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, keep it in the live `P4-L24` matrix reminder lane; if the drift is limited to the dedicated remaining-gap checker falling behind those already-landed markers, keep it in the live `P4-L19` checker-maintenance lane before reopening either parked starter-gap packet.",
    "reopen the dedicated perf lane only for one checker, manifest, survey, benchmark-command, acceptable-limit, or local-only policy truthfulness repair",
};

const REVERSIBLE_MARKERS = [_][]const u8{
    "Current direct readback in this run confirmed this note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_tests_readme_packet.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, `scripts\\zigux/check_phase4_workflow_route_counts.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "The broader Phase 4 validator, build, and bitmap replay companions are no longer safe to describe as current-`master` gaps in this handoff.",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig`, `zigux/tests/runtime_atomic64_diff.zig`, `zigux/tests/phase4_runtime_atomic64_diff_manifest.json`, and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` now return on current `master`",
};

const REPO_WARNING_MARKERS = [_][]const u8{
    "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32",
    "EXPECTED_PIN_SELF_TEST_CASES = 20",
    "SEQUENCING_NOTE = Path(\"Documentation/zigux/phase4-validation-lane-sequencing.md\")",
    "REMAINING_GAP_PACKET = (",
    "    \"scripts\\zigux/validate_phase4.zig\",",
    "    \"zigux/tests/phase4_build.zig\",",
};

const PERF_PACKET_MARKERS = [_][]const u8{
    "EXPECTED_SELF_TEST_CASES = 39",
    "MANIFEST = Path(\"zigux/tests/phase4_perf_baseline_manifest.json\")",
    "REVIEW_CHECKLIST_MARKERS = (",
    "NOTE_MARKERS = (",
    "Current direct-readback dedicated local-only perf checkers: `scripts\\zigux/check_phase4_perf_baseline_packet.zig` and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`.",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_sequencing_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-lane-sequencing.md");
    defer allocator.free(text_sequencing_markers_path);
    const text_sequencing_markers = try guard.readUtf8File(io, allocator, text_sequencing_markers_path);
    defer allocator.free(text_sequencing_markers);
    for (SEQUENCING_MARKERS) |marker| try guard.requireMarker(text_sequencing_markers, marker);
    const text_reversible_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-lane-sequencing.md");
    defer allocator.free(text_reversible_markers_path);
    const text_reversible_markers = try guard.readUtf8File(io, allocator, text_reversible_markers_path);
    defer allocator.free(text_reversible_markers);
    for (REVERSIBLE_MARKERS) |marker| try guard.requireMarker(text_reversible_markers, marker);
    const text_repo_warning_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase4_repo_reality_warning.zig");
    defer allocator.free(text_repo_warning_markers_path);
    const text_repo_warning_markers = try guard.readUtf8File(io, allocator, text_repo_warning_markers_path);
    defer allocator.free(text_repo_warning_markers);
    for (REPO_WARNING_MARKERS) |marker| try guard.requireMarker(text_repo_warning_markers, marker);
    const text_perf_packet_markers_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase4_perf_baseline_packet.zig");
    defer allocator.free(text_perf_packet_markers_path);
    const text_perf_packet_markers = try guard.readUtf8File(io, allocator, text_perf_packet_markers_path);
    defer allocator.free(text_perf_packet_markers);
    for (PERF_PACKET_MARKERS) |marker| try guard.requireMarker(text_perf_packet_markers, marker);
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
