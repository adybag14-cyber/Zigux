const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectNotContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) == null);
}

fn section(source: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, source, start_marker) orelse return error.MissingSectionStart;
    const end = std.mem.indexOfPos(u8, source, start + start_marker.len, end_marker) orelse return error.MissingSectionEnd;
    return source[start..end];
}

test "phase4 test_fsmount survey keeps dedicated phase4 build route but not aggregate replay" {
    const phase4_build = try readRepoFile("zigux/tests/phase4_build.zig");
    defer std.testing.allocator.free(phase4_build);

    try expectContains(phase4_build, ".root_source_file = b.path(\"phase4_test_fsmount_survey.zig\")");
    try expectContains(phase4_build, ".name = \"phase4-test-fsmount-survey-tests\"");
    try expectContains(phase4_build, "const test_fsmount_survey_step = b.step(");
    try expectContains(phase4_build, "\"phase4-test-fsmount-survey\"");
    try expectContains(phase4_build, "Run the dedicated Phase 4 test_fsmount gap survey without promoting a shipped Zig starter");
    try expectContains(phase4_build, "test_fsmount_survey_step.dependOn(&run_test_fsmount_survey_tests.step);");

    const aggregate = try section(
        phase4_build,
        "const test_step = b.step(\"test\", \"Run Phase 4 differential validation tests\");",
        "const runtime_atomic64_diff_step = b.step(",
    );
    try expectNotContains(aggregate, "run_test_fsmount_survey_tests");
    try expectNotContains(aggregate, "phase4-test-fsmount-survey-tests");
}

test "phase4 test_fsmount contract keeps shared root and make-wrapper wording aligned" {
    const tests_readme = try readRepoFile("zigux/tests/README.md");
    defer std.testing.allocator.free(tests_readme);
    const scripts_readme = try readRepoFile("scripts/zigux/README.md");
    defer std.testing.allocator.free(scripts_readme);
    const gate_evidence = try readRepoFile("Documentation/zigux/phase4-gate-evidence.md");
    defer std.testing.allocator.free(gate_evidence);
    const validation_matrix = try readRepoFile("Documentation/zigux/phase4-validation-matrix.md");
    defer std.testing.allocator.free(validation_matrix);

    const local_wrapper = "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig";
    const make_wrapper = "make -C zigux phase4-test-fsmount-survey";

    try expectContains(tests_readme, "zigux/tests/phase4_test_fsmount_manifest.json");
    try expectContains(tests_readme, "zigux/tests/phase4_test_fsmount_survey.zig");
    try expectContains(tests_readme, local_wrapper);
    try expectContains(tests_readme, make_wrapper);
    try expectContains(tests_readme, "samples/zigux/test_fsmount.zig");

    try expectContains(scripts_readme, local_wrapper);
    try expectContains(scripts_readme, make_wrapper);
    try expectContains(gate_evidence, "PHASE4_SHARED_TEST_FSMOUNT_SURVEY_PACKET_PRESENT=true");
    try expectContains(gate_evidence, "test_fsmount_validation_entrypoint_drift");
    try expectContains(validation_matrix, "phase4-test-fsmount-survey");
    try expectContains(validation_matrix, "reviewability_only_no_perf_threshold");
}

test "phase4 test_fsmount manifest and survey keep absent-starter boundary explicit" {
    const manifest = try readRepoFile("zigux/tests/phase4_test_fsmount_manifest.json");
    defer std.testing.allocator.free(manifest);
    const survey = try readRepoFile("zigux/tests/phase4_test_fsmount_survey.zig");
    defer std.testing.allocator.free(survey);
    const note = try readRepoFile("Documentation/zigux/phase4-test-fsmount-gap-survey.md");
    defer std.testing.allocator.free(note);

    try expectContains(manifest, "\"lane_key\": \"P4-L19\"");
    try expectContains(manifest, "\"c_anchor\": \"samples/vfs/test-fsmount.c\"");
    try expectContains(manifest, "\"dedicated_local_survey_wrapper\": \"zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig\"");
    try expectContains(manifest, "\"dedicated_linux_style_survey_wrapper\": \"make -C zigux phase4-test-fsmount-survey\"");
    try expectContains(manifest, "\"threshold_posture\": \"reviewability_only_no_perf_threshold\"");
    try expectContains(manifest, "\"current_measurable_status\": \"absent_on_current_master_but_reviewable_through_the_dedicated_gap_packet_without_claiming_a_shipped_zig_starter\"");

    try expectContains(survey, "phase4 test_fsmount survey manifest records the parked survey packet and remaining sample gap");
    try expectContains(survey, "tests_readme_present");
    try expectContains(note, "Current `master` still does not ship `samples/zigux/test_fsmount.zig`.");
}
