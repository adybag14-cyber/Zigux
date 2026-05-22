const std = @import("std");

const current_surveyed_commit = "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3";

const SurveySummary = struct {
    zig_sample_present: bool,
    phase4_build_present: bool,
    phase4_validation_matrix_present: bool,
    phase4_gate_evidence_present: bool,
    scripts_readme_present: bool,
    tests_readme_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    c_anchor: []const u8,
    roadmap_destinations: []const []const u8,
    current_linux_replay: []const u8,
    dedicated_local_survey_wrapper: []const u8,
    dedicated_linux_style_survey_wrapper: []const u8,
    shared_build_replay: []const u8,
    bootstrap_ci_posture: []const u8,
    shared_lab_and_ci_matrix_anchor: []const u8,
    validation_entrypoint: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    current_measurable_status: []const u8,
    threshold_posture: []const u8,
    reversible_delivery_evidence: []const u8,
    next_bounded_evidence_step: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or std.mem.eql(u8, status, "ready_next");
}

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

test "phase4 test_fsmount survey manifest records the parked survey packet and remaining sample gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_test_fsmount_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P4-L19", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 4", manifest.phase);
    try std.testing.expect(isLowerHexSha(current_surveyed_commit));
    try std.testing.expectEqualStrings(current_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expectEqualStrings("samples/vfs/test-fsmount.c", manifest.c_anchor);
    try std.testing.expectEqualStrings("make M=samples/vfs", manifest.current_linux_replay);
    try std.testing.expectEqualStrings("zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig", manifest.dedicated_local_survey_wrapper);
    try std.testing.expectEqualStrings("make -C zigux phase4-test-fsmount-survey", manifest.dedicated_linux_style_survey_wrapper);
    try std.testing.expectEqualStrings("phase4-test-fsmount-survey-tests", manifest.shared_build_replay);
    try std.testing.expectEqualStrings("reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow", manifest.bootstrap_ci_posture);
    try std.testing.expectEqualStrings("Documentation/zigux/phase4-validation-matrix.md#lab-and-ci-matrix", manifest.shared_lab_and_ci_matrix_anchor);
    try std.testing.expectEqualStrings("zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig", manifest.validation_entrypoint);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.owner);
    try std.testing.expectEqualStrings("Validation and Perf Team", manifest.rollback_owner);
    try std.testing.expectEqualStrings("absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter", manifest.current_measurable_status);
    try std.testing.expectEqualStrings("reviewability_only_no_perf_threshold", manifest.threshold_posture);
    try std.testing.expectEqualStrings("PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface", manifest.reversible_delivery_evidence);
    try std.testing.expectEqualStrings("keep the dedicated parked survey packet adjacent to the shared gate-evidence note, the shared Phase 4 exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the explicit reviewability-only no-perf-threshold posture, the dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey` wrapper until a later bounded lane intentionally promotes the validator surface or lands the Zig starter", manifest.next_bounded_evidence_step);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("samples/zigux/test_fsmount.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqual(@as(usize, 5), manifest.gaps.len);

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);
    const phase4_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase4_build.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase4_build);
    const phase4_matrix = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-validation-matrix.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase4_matrix);
    const phase4_gate_evidence = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase4-gate-evidence.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase4_gate_evidence);
    const scripts_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(scripts_readme);
    const tests_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/README.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(tests_readme);

    const zig_sample_present = blk: {
        std.Io.Dir.cwd().access(io_instance.io(), "samples/zigux/test_fsmount.zig", .{}) catch |err| switch (err) {
            error.FileNotFound => break :blk false,
            else => return err,
        };
        break :blk true;
    };

    const live_summary = SurveySummary{
        .zig_sample_present = zig_sample_present,
        .phase4_build_present = std.mem.indexOf(u8, phase4_build, "phase4_test_fsmount_survey.zig") != null and
            std.mem.indexOf(u8, phase4_build, manifest.shared_build_replay) != null and
            std.mem.indexOf(u8, phase4_build, "phase4-test-fsmount-survey") != null,
        .phase4_validation_matrix_present = std.mem.indexOf(u8, phase4_matrix, "phase4_test_fsmount_manifest.json") != null and
            std.mem.indexOf(u8, phase4_matrix, "phase4_test_fsmount_survey.zig") != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.validation_entrypoint) != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.dedicated_linux_style_survey_wrapper) != null and
            std.mem.indexOf(u8, phase4_matrix, manifest.threshold_posture) != null and
            std.mem.indexOf(u8, phase4_matrix, "samples/zigux/test_fsmount.zig") != null,
        .phase4_gate_evidence_present = std.mem.indexOf(u8, phase4_gate_evidence, "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true") != null and
            std.mem.indexOf(u8, phase4_gate_evidence, "test_fsmount_gap_packet_presence_drift") != null and
            std.mem.indexOf(u8, phase4_gate_evidence, "test_fsmount_threshold_posture_drift") != null and
            std.mem.indexOf(u8, phase4_gate_evidence, "test_fsmount_validation_entrypoint_drift") != null and
            std.mem.indexOf(u8, phase4_gate_evidence, "test_fsmount_linux_style_wrapper_drift") != null and
            std.mem.indexOf(u8, phase4_gate_evidence, "test_fsmount_next_step_drift") != null,
        .scripts_readme_present = std.mem.indexOf(u8, scripts_readme, "phase4-test-fsmount-survey-tests") != null,
        .tests_readme_present = std.mem.indexOf(u8, tests_readme, "make -C zigux phase4-test-fsmount-survey") != null and
            std.mem.indexOf(u8, tests_readme, "c_anchor_only_until_test_fsmount_starter_lands") != null,
    };
    try std.testing.expectEqualDeep(live_summary, manifest.survey_summary);

    try std.testing.expect(std.mem.indexOf(u8, note, manifest.reversible_delivery_evidence) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, manifest.next_bounded_evidence_step) != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.") != null);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_validator_promotion_gap = false;
    var saw_sample_gap = false;
    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));
        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, gap.status, "ready_next")) ready_next_count += 1;
        if (std.mem.eql(u8, gap.id, "phase4-test-fsmount-shared-validator-promotion")) {
            saw_validator_promotion_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase4-test-fsmount-survey-tests") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase4-test-fsmount-zig-sample")) {
            saw_sample_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/test_fsmount.zig", gap.zigux_destination);
        }
        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 4), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expect(saw_validator_promotion_gap);
    try std.testing.expect(saw_sample_gap);
}
