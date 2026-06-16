const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_SHARED_REMINDER_SURFACES_CHECK=pass";
pub const self_test_pass_marker = "PHASE4_SHARED_REMINDER_SURFACES_SELF_TEST=pass";

const NOTE_MARKERS = [_][]const u8{
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "Current direct contents reads in this run also confirmed the roadmap-backed differential-gate pair `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` on current `master`.",
    "Current direct contents reads in this run also confirmed `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`, `scripts\\zigux/check_phase4_workflow_route_counts.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` on current `master`",
    "public raw fallback rereads now return those files on current `master`",
    "The remaining shared reminder follow-up from the older mixed-readback packet is now narrower: `zigux/tests/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `scripts/zigux/README.md` should align",
};

const DOCS_README_MARKERS = [_][]const u8{
    "Phase 4 notes - `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`scripts\\zigux/check_phase4_workflow_route_counts.zig`",
    "`scripts\\zigux/check_phase4_perf_baseline_packet.zig`",
    "`scripts\\zigux/validate_phase4.zig`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/tests/bitmap_diff.zig`",
    "`zigux/tests/phase4_bitmap_live_helper_replay.zig`",
    "keep the bounded Phase 4 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle",
};

const CHECKLIST_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts\\zigux/check_phase4_repo_reality_warning.zig` and `scripts\\zigux/check_phase4_reversible_delivery_pins.zig` still agree on the current direct-readback packet",
    "keep the directly readable local-only perf packet explicit",
    "keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, and `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "keep the repo-reality warning explicit for the broader Phase 4 validator, build, and bitmap-diff companions still needing raw-fallback proof or fresh authenticated blob capture",
    "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
    "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    "keep the ABI and Runtime Team plus Shared Subsystems Pod as coordination owners for that policy call",
    "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase4_artifact_diff_validator_replays.zig`",
    "`scripts\\zigux/check_phase4_perf_baseline_packet.zig`",
    "`scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "`scripts\\zigux/check_phase4_workflow_route_counts.zig`",
    "`scripts\\zigux/validate_phase4.zig`, `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap in authenticated contents reads in this runtime, but public raw fallback rereads return those files on current `master`",
    "keep them explicit as now-returned companions while exact authenticated blob-pin refresh remains pending",
    "keep Phase 4 follow-through narrowed to one reminder-surface, contract, checker, rollback-owner, or local-only perf-governance truthfulness repair at a time",
};

const TESTS_README_MARKERS = [_][]const u8{
    "Keep the current bounded Phase 4 reminder packet explicit through `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `scripts\\zigux/check_phase4_repo_reality_warning.zig`, `scripts\\zigux/check_phase4_reversible_delivery_pins.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, and `zigux/tests/README.md`.",
    "Keep the recovered broader note-and-checker companions explicit through `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, `scripts\\zigux/check_phase4_gate_evidence.zig`, and `scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "Current direct-readback dedicated local-only perf checker: `scripts\\zigux/check_phase4_perf_baseline_packet.zig`",
    "Current direct-readback dedicated local-only perf companion members: `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-reversible-delivery-evidence.md");
    defer allocator.free(text_note_markers_path);
    const text_note_markers = try guard.readUtf8File(io, allocator, text_note_markers_path);
    defer allocator.free(text_note_markers);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text_note_markers, marker);
    const text_docs_readme_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_docs_readme_markers_path);
    const text_docs_readme_markers = try guard.readUtf8File(io, allocator, text_docs_readme_markers_path);
    defer allocator.free(text_docs_readme_markers);
    for (DOCS_README_MARKERS) |marker| try guard.requireMarker(text_docs_readme_markers, marker);
    const text_checklist_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-reversible-delivery-evidence.md");
    defer allocator.free(text_checklist_markers_path);
    const text_checklist_markers = try guard.readUtf8File(io, allocator, text_checklist_markers_path);
    defer allocator.free(text_checklist_markers);
    for (CHECKLIST_MARKERS) |marker| try guard.requireMarker(text_checklist_markers, marker);
    const text_scripts_readme_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/README.md");
    defer allocator.free(text_scripts_readme_markers_path);
    const text_scripts_readme_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_markers_path);
    defer allocator.free(text_scripts_readme_markers);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_markers, marker);
    const text_tests_readme_markers_path = try guard.joinPath(allocator, root, "zigux/tests/README.md");
    defer allocator.free(text_tests_readme_markers_path);
    const text_tests_readme_markers = try guard.readUtf8File(io, allocator, text_tests_readme_markers_path);
    defer allocator.free(text_tests_readme_markers);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text_tests_readme_markers, marker);
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
