const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_REMAINING_GAP_MATRIX=pass";
pub const self_test_pass_marker = "PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=pass";

const KPROBE_SURVEYED_COMMIT = [_][]const u8{
    "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3",
};

const TEST_FSMOUNT_SURVEYED_COMMIT = [_][]const u8{
    "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3",
};

const KPROBE_SHARED_BUILD_REPLAY = [_][]const u8{
    "phase4-kprobe-example-survey-tests",
};

const TEST_FSMOUNT_SHARED_BUILD_REPLAY = [_][]const u8{
    "phase4-test-fsmount-survey-tests",
};

const KPROBE_MATRIX_ANCHOR = [_][]const u8{
    "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
};

const TEST_FSMOUNT_MATRIX_ANCHOR = [_][]const u8{
    "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
};

const PERF_MATRIX_ANCHOR = [_][]const u8{
    "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
};

const KPROBE_REVERSIBLE_DELIVERY_EVIDENCE = [_][]const u8{
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the explicit bootstrap-CI posture, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded starter lane intentionally widens this surface",
};

const KPROBE_NEXT_BOUNDED_EVIDENCE_STEP = [_][]const u8{
    "Keep this parked packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the dedicated local `make -C zigux phase4-kprobe-example-survey` wrapper, and the direct `zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint until a later bounded Phase 4 lane lands the actual Zig starter with an updated rollback-readiness contract.",
};

const TEST_FSMOUNT_REVERSIBLE_DELIVERY_EVIDENCE = [_][]const u8{
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
};

const TEST_FSMOUNT_NEXT_BOUNDED_EVIDENCE_STEP = [_][]const u8{
    "keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter",
};

const MATRIX_MARKERS = [_][]const u8{
    "`scripts\\zigux/check_phase4_remaining_gap_matrix.zig`",
    "`Documentation/zigux/phase4-measurability-gap-survey.md`",
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`",
    "`zigux/tests/phase4_kprobe_example_manifest.json`",
    "`zigux/tests/phase4_kprobe_example_survey.zig`",
    "`make -C zigux phase4-kprobe-example-survey`",
    "c_anchor_only_until_kprobe_example_starter_lands",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
    "`zigux/tests/phase4_test_fsmount_manifest.json`",
    "`zigux/tests/phase4_test_fsmount_survey.zig`",
    "`zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "`make -C zigux phase4-test-fsmount-survey`",
    "reviewability_only_no_perf_threshold",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "shared CI perf promotion pending",
    "`zig run scripts\\zigux/check_phase4_perf_baseline_packet.zig --self-test` then `zig run scripts\\zigux/check_phase4_perf_baseline_packet.zig`",
    "Validation and Perf Team owning that policy decision",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
};

const MEASURABILITY_GAP_NOTE_MARKERS = [_][]const u8{
    "# Phase 4 Measurability Gap Survey",
    "PHASE4_MEASURABILITY_GAP_REMAINING_PACKET_COUNT=3",
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`",
    "`Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, and `scripts\\zigux/validate_phase4.zig`",
};

const KPROBE_NOTE_MARKERS = [_][]const u8{
    "PHASE4_KPROBE_STATUS=parked_gap_packet_landed",
    "PHASE4_KPROBE_LANE_KEY=P4-L19",
    "PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c",
    "PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow",
    "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "PHASE4_KPROBE_OWNER=Validation and Perf Team",
    "PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team",
    "Current `master` still does not ship `samples/zigux/kprobe_example.zig`.",
};

const TEST_FSMOUNT_NOTE_MARKERS = [_][]const u8{
    "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed",
    "PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19",
    "PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c",
    "PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs",
    "PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey",
    "PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow",
    "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
    "PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold",
    "PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team",
    "PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team",
    "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.",
};

const PHASE4_BUILD_MARKERS = [_][]const u8{
    "phase4_test_fsmount_survey.zig",
    "phase4-test-fsmount-survey",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_kprobe_surveyed_commit_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_kprobe_surveyed_commit_path);
    const text_kprobe_surveyed_commit = try guard.readUtf8File(io, allocator, text_kprobe_surveyed_commit_path);
    defer allocator.free(text_kprobe_surveyed_commit);
    for (KPROBE_SURVEYED_COMMIT) |marker| try guard.requireMarker(text_kprobe_surveyed_commit, marker);
    const text_test_fsmount_surveyed_commit_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_test_fsmount_surveyed_commit_path);
    const text_test_fsmount_surveyed_commit = try guard.readUtf8File(io, allocator, text_test_fsmount_surveyed_commit_path);
    defer allocator.free(text_test_fsmount_surveyed_commit);
    for (TEST_FSMOUNT_SURVEYED_COMMIT) |marker| try guard.requireMarker(text_test_fsmount_surveyed_commit, marker);
    const text_kprobe_shared_build_replay_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_kprobe_shared_build_replay_path);
    const text_kprobe_shared_build_replay = try guard.readUtf8File(io, allocator, text_kprobe_shared_build_replay_path);
    defer allocator.free(text_kprobe_shared_build_replay);
    for (KPROBE_SHARED_BUILD_REPLAY) |marker| try guard.requireMarker(text_kprobe_shared_build_replay, marker);
    const text_test_fsmount_shared_build_replay_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_test_fsmount_shared_build_replay_path);
    const text_test_fsmount_shared_build_replay = try guard.readUtf8File(io, allocator, text_test_fsmount_shared_build_replay_path);
    defer allocator.free(text_test_fsmount_shared_build_replay);
    for (TEST_FSMOUNT_SHARED_BUILD_REPLAY) |marker| try guard.requireMarker(text_test_fsmount_shared_build_replay, marker);
    const text_kprobe_matrix_anchor_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_kprobe_matrix_anchor_path);
    const text_kprobe_matrix_anchor = try guard.readUtf8File(io, allocator, text_kprobe_matrix_anchor_path);
    defer allocator.free(text_kprobe_matrix_anchor);
    for (KPROBE_MATRIX_ANCHOR) |marker| try guard.requireMarker(text_kprobe_matrix_anchor, marker);
    const text_test_fsmount_matrix_anchor_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_test_fsmount_matrix_anchor_path);
    const text_test_fsmount_matrix_anchor = try guard.readUtf8File(io, allocator, text_test_fsmount_matrix_anchor_path);
    defer allocator.free(text_test_fsmount_matrix_anchor);
    for (TEST_FSMOUNT_MATRIX_ANCHOR) |marker| try guard.requireMarker(text_test_fsmount_matrix_anchor, marker);
    const text_perf_matrix_anchor_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_perf_matrix_anchor_path);
    const text_perf_matrix_anchor = try guard.readUtf8File(io, allocator, text_perf_matrix_anchor_path);
    defer allocator.free(text_perf_matrix_anchor);
    for (PERF_MATRIX_ANCHOR) |marker| try guard.requireMarker(text_perf_matrix_anchor, marker);
    const text_kprobe_reversible_delivery_evidence_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_kprobe_reversible_delivery_evidence_path);
    const text_kprobe_reversible_delivery_evidence = try guard.readUtf8File(io, allocator, text_kprobe_reversible_delivery_evidence_path);
    defer allocator.free(text_kprobe_reversible_delivery_evidence);
    for (KPROBE_REVERSIBLE_DELIVERY_EVIDENCE) |marker| try guard.requireMarker(text_kprobe_reversible_delivery_evidence, marker);
    const text_kprobe_next_bounded_evidence_step_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_kprobe_next_bounded_evidence_step_path);
    const text_kprobe_next_bounded_evidence_step = try guard.readUtf8File(io, allocator, text_kprobe_next_bounded_evidence_step_path);
    defer allocator.free(text_kprobe_next_bounded_evidence_step);
    for (KPROBE_NEXT_BOUNDED_EVIDENCE_STEP) |marker| try guard.requireMarker(text_kprobe_next_bounded_evidence_step, marker);
    const text_test_fsmount_reversible_delivery_evidence_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_test_fsmount_reversible_delivery_evidence_path);
    const text_test_fsmount_reversible_delivery_evidence = try guard.readUtf8File(io, allocator, text_test_fsmount_reversible_delivery_evidence_path);
    defer allocator.free(text_test_fsmount_reversible_delivery_evidence);
    for (TEST_FSMOUNT_REVERSIBLE_DELIVERY_EVIDENCE) |marker| try guard.requireMarker(text_test_fsmount_reversible_delivery_evidence, marker);
    const text_test_fsmount_next_bounded_evidence_step_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_test_fsmount_next_bounded_evidence_step_path);
    const text_test_fsmount_next_bounded_evidence_step = try guard.readUtf8File(io, allocator, text_test_fsmount_next_bounded_evidence_step_path);
    defer allocator.free(text_test_fsmount_next_bounded_evidence_step);
    for (TEST_FSMOUNT_NEXT_BOUNDED_EVIDENCE_STEP) |marker| try guard.requireMarker(text_test_fsmount_next_bounded_evidence_step, marker);
    const text_matrix_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-validation-matrix.md");
    defer allocator.free(text_matrix_markers_path);
    const text_matrix_markers = try guard.readUtf8File(io, allocator, text_matrix_markers_path);
    defer allocator.free(text_matrix_markers);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text_matrix_markers, marker);
    const text_measurability_gap_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-measurability-gap-survey.md");
    defer allocator.free(text_measurability_gap_note_markers_path);
    const text_measurability_gap_note_markers = try guard.readUtf8File(io, allocator, text_measurability_gap_note_markers_path);
    defer allocator.free(text_measurability_gap_note_markers);
    for (MEASURABILITY_GAP_NOTE_MARKERS) |marker| try guard.requireMarker(text_measurability_gap_note_markers, marker);
    const text_kprobe_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-kprobe-example-gap-survey.md");
    defer allocator.free(text_kprobe_note_markers_path);
    const text_kprobe_note_markers = try guard.readUtf8File(io, allocator, text_kprobe_note_markers_path);
    defer allocator.free(text_kprobe_note_markers);
    for (KPROBE_NOTE_MARKERS) |marker| try guard.requireMarker(text_kprobe_note_markers, marker);
    const text_test_fsmount_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase4-test-fsmount-gap-survey.md");
    defer allocator.free(text_test_fsmount_note_markers_path);
    const text_test_fsmount_note_markers = try guard.readUtf8File(io, allocator, text_test_fsmount_note_markers_path);
    defer allocator.free(text_test_fsmount_note_markers);
    for (TEST_FSMOUNT_NOTE_MARKERS) |marker| try guard.requireMarker(text_test_fsmount_note_markers, marker);
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
