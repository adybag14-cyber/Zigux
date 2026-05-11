const std = @import("std");

const manifest_source = @embedFile("phase14_end_to_end_smoke_manifest.json");
const build_source = @embedFile("phase14_build.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readSurveySource() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
}

test "phase14 shared smoke manifest keeps workqueue reviewability explicit" {
    try expectContains(manifest_source, "\"zigux/tests/phase14_workqueue_reviewability.zig\"");
    try expectContains(manifest_source, "\"label\": \"phase14-workqueue-reviewability-tests\"");
    try expectContains(manifest_source, "\"root_source\": \"phase14_workqueue_reviewability.zig\"");
    try expectContains(manifest_source, "\"coverage\": \"full_bundle_only\"");
}

test "phase14 build wires workqueue reviewability into the full bundle only" {
    try expectContains(build_source, ".root_source_file = b.path(\"phase14_workqueue_reviewability.zig\")");
    try expectContains(build_source, ".name = \"phase14-workqueue-reviewability-tests\"");
    try expectContains(build_source, "test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);");
    try std.testing.expect(std.mem.indexOf(u8, build_source, "smoke_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);") == null);
}

test "phase14 survey keeps the reviewability shard in the shared smoke packet" {
    const survey_source = try readSurveySource();
    defer std.testing.allocator.free(survey_source);

    try expectContains(survey_source, "`zigux/tests/phase14_workqueue_reviewability.zig`");
    try expectContains(survey_source, "`phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`");
    try expectContains(survey_source, "focused workqueue reviewability replay");
}
