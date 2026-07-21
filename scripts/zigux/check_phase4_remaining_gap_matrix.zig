const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE4_REMAINING_GAP_MATRIX=pass";
pub const self_test_pass_marker = "PHASE4_REMAINING_GAP_MATRIX_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3",
    "phase4-kprobe-example-survey-tests",
    "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the explicit bootstrap-CI posture, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded starter lane intentionally widens this surface",
    "Keep this parked packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the dedicated local `make -C zigux phase4-kprobe-example-survey` wrapper, and the direct `zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint until a later bounded Phase 4 lane lands the actual Zig starter with an updated rollback-readiness contract.",
};

const markers_1 = [_][]const u8{
    "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3",
    "phase4-test-fsmount-survey-tests",
    "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface",
    "keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter",
};

const markers_2 = [_][]const u8{
    "Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix",
};

const markers_3 = [_][]const u8{
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
    "Validation and Perf Team owning that policy decision",
    "gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
    "rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`",
};

const markers_4 = [_][]const u8{
    "# Phase 4 Measurability Gap Survey",
    "PHASE4_MEASURABILITY_GAP_REMAINING_PACKET_COUNT=3",
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `scripts\\zigux/check_phase4_perf_baseline_packet.zig`, and `scripts\\zigux/check_phase4_perf_threshold_matrix.zig`",
    "`Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, and `scripts\\zigux/validate_phase4.zig`",
};

const markers_5 = [_][]const u8{
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

const markers_6 = [_][]const u8{
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

const markers_7 = [_][]const u8{
    "phase4_test_fsmount_survey.zig",
    "phase4-test-fsmount-survey",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/tests/phase4_kprobe_example_manifest.json", .markers = &markers_0 },
    .{ .rel = "zigux/tests/phase4_test_fsmount_manifest.json", .markers = &markers_1 },
    .{ .rel = "zigux/tests/phase4_perf_baseline_manifest.json", .markers = &markers_2 },
    .{ .rel = "Documentation/zigux/phase4-validation-matrix.md", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase4-measurability-gap-survey.md", .markers = &markers_4 },
    .{ .rel = "Documentation/zigux/phase4-kprobe-example-gap-survey.md", .markers = &markers_5 },
    .{ .rel = "Documentation/zigux/phase4-test-fsmount-gap-survey.md", .markers = &markers_6 },
    .{ .rel = "zigux/tests/phase4_build.zig", .markers = &markers_7 },
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
    try guard.printLine(io, "PHASE4_REMAINING_GAP_MATRIX_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 8)});
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
// KPROBE_SURVEYED_COMMIT
// 3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3
// TEST_FSMOUNT_SURVEYED_COMMIT
// 3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3
// KPROBE_SHARED_BUILD_REPLAY
// phase4-kprobe-example-survey-tests
// TEST_FSMOUNT_SHARED_BUILD_REPLAY
// phase4-test-fsmount-survey-tests
// KPROBE_MATRIX_ANCHOR
// Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix
// TEST_FSMOUNT_MATRIX_ANCHOR
// Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix
// PERF_MATRIX_ANCHOR
// Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix
// KPROBE_REVERSIBLE_DELIVERY_EVIDENCE
// PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the explicit bootstrap-CI posture, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded starter lane intentionally widens this surface
// KPROBE_NEXT_BOUNDED_EVIDENCE_STEP
// Keep this parked packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the dedicated local `make -C zigux phase4-kprobe-example-survey` wrapper, and the direct `zig test zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint until a later bounded Phase 4 lane lands the actual Zig starter with an updated rollback-readiness contract.
// TEST_FSMOUNT_REVERSIBLE_DELIVERY_EVIDENCE
// PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface
// TEST_FSMOUNT_NEXT_BOUNDED_EVIDENCE_STEP
// keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit local lab replay marker, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter
// MATRIX_MARKERS
// `scripts\zigux/check_phase4_remaining_gap_matrix.zig`
// `Documentation/zigux/phase4-measurability-gap-survey.md`
// `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
// `zigux/tests/phase4_kprobe_example_manifest.json`
// `zigux/tests/phase4_kprobe_example_survey.zig`
// `make -C zigux phase4-kprobe-example-survey`
// c_anchor_only_until_kprobe_example_starter_lands
// `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
// `zigux/tests/phase4_test_fsmount_manifest.json`
// `zigux/tests/phase4_test_fsmount_survey.zig`
// `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
// `make -C zigux phase4-test-fsmount-survey`
// reviewability_only_no_perf_threshold
// `zigux/tests/phase4_perf_baseline_manifest.json`
// shared CI perf promotion pending
// `zig run scripts\zigux/check_phase4_perf_baseline_packet.zig -- --self-test` then `zig run scripts\zigux/check_phase4_perf_baseline_packet.zig`
// Validation and Perf Team owning that policy decision
// gate owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
// rollback owners: `ABI and Runtime Team` and `Shared Subsystems Pod`
// MEASURABILITY_GAP_NOTE_MARKERS
// # Phase 4 Measurability Gap Survey
// PHASE4_MEASURABILITY_GAP_REMAINING_PACKET_COUNT=3
// `Documentation/zigux/phase4-kprobe-example-gap-survey.md`, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`
// `Documentation/zigux/phase4-test-fsmount-gap-survey.md`, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`
// `zigux/tests/phase4_perf_baseline_manifest.json`, `zigux/tests/phase4_perf_baseline_survey.zig`, `scripts\zigux/check_phase4_perf_baseline_packet.zig`, and `scripts\zigux/check_phase4_perf_threshold_matrix.zig`
// `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-reversible-delivery-evidence.md`, and `scripts\zigux/validate_phase4.zig`
// KPROBE_NOTE_MARKERS
// PHASE4_KPROBE_STATUS=parked_gap_packet_landed
// PHASE4_KPROBE_LANE_KEY=P4-L19
// PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c
// PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m
// PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey
// PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey
// PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow
// PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig
// PHASE4_KPROBE_OWNER=Validation and Perf Team
// PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team
// Current `master` still does not ship `samples/zigux/kprobe_example.zig`.
// TEST_FSMOUNT_NOTE_MARKERS
// PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed
// PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19
// PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c
// PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs
// PHASE4_TEST_FSMOUNT_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
// PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
// PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey
// PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow
// PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig
// PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold
// PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team
// PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team
// Current `master` still does not ship `samples/zigux/test_fsmount.zig`.
// PHASE4_BUILD_MARKERS
// phase4_test_fsmount_survey.zig
// phase4-test-fsmount-survey
// DROPPED_STALE_OWNER_MARKERS
// Documentation/zigux/phase4-validation-matrix.md: `zig run scripts\zigux/check_phase4_perf_baseline_packet.zig -- --self-test` then `zig run scripts\zigux/check_phase4_perf_baseline_packet.zig`
