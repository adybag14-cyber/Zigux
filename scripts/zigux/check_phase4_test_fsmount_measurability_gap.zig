const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP=pass";
pub const self_test_pass_marker = "PHASE4_TEST_FSMOUNT_MEASURABILITY_GAP_SELF_TEST=pass";

const EXPECTED_NOTE_MARKERS = [_][]const u8{
    "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed",
    "PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19",
    "PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c",
    "PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs",
    "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
    "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
    "PHASE4_TEST_FSMOUNT_SHARED_LAB_AND_CI_MATRIX_ANCHOR=Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
    "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
    "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.",
};

const EXPECTED_MATRIX_MARKERS = [_][]const u8{
    "* current replay path: `make M=samples/vfs`",
    "* dedicated local survey wrapper: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "* dedicated Linux-style survey wrapper: `make -C zigux phase4-test-fsmount-survey`",
    "* validation entrypoint: `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "* survey owner: `Validation and Perf Team`",
    "* rollback owner: `Validation and Perf Team`",
    "reviewability_only_no_perf_threshold",
};

const EXPECTED_GATE_EVIDENCE_MARKERS = [_][]const u8{
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "make -C zigux phase4-test-fsmount-survey",
    "reviewability_only_no_perf_threshold",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-test-fsmount-gap-survey.md");
    defer allocator.free(text_expected_note_markers_path);
    const text_expected_note_markers = try guard.readUtf8File(io, allocator, text_expected_note_markers_path);
    defer allocator.free(text_expected_note_markers);
    for (EXPECTED_NOTE_MARKERS) |marker| try guard.requireMarker(text_expected_note_markers, marker);
    const text_expected_matrix_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-test-fsmount-gap-survey.md");
    defer allocator.free(text_expected_matrix_markers_path);
    const text_expected_matrix_markers = try guard.readUtf8File(io, allocator, text_expected_matrix_markers_path);
    defer allocator.free(text_expected_matrix_markers);
    for (EXPECTED_MATRIX_MARKERS) |marker| try guard.requireMarker(text_expected_matrix_markers, marker);
    const text_expected_gate_evidence_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-test-fsmount-gap-survey.md");
    defer allocator.free(text_expected_gate_evidence_markers_path);
    const text_expected_gate_evidence_markers = try guard.readUtf8File(io, allocator, text_expected_gate_evidence_markers_path);
    defer allocator.free(text_expected_gate_evidence_markers);
    for (EXPECTED_GATE_EVIDENCE_MARKERS) |marker| try guard.requireMarker(text_expected_gate_evidence_markers, marker);
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
