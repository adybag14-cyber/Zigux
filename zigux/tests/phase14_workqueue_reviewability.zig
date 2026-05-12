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

fn readTraceabilitySource() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-core-boundary-traceability.md",
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

test "phase14 shared smoke packet keeps the current workqueue anchor metadata aligned" {
    const survey_source = try readSurveySource();
    defer std.testing.allocator.free(survey_source);

    try expectContains(manifest_source, "\"lane_key\": \"P14-L04\"");
    try expectContains(manifest_source, "\"surveyed_commit\": \"9b98d3b9c812840bf279508030be0b8de093736c\"");
    try expectContains(manifest_source, "\"ready_next_gap\": \"\"");
    try expectContains(manifest_source, "\"blocked_gap\": \"phase14-workqueue-live-execution-blocker\"");
    try std.testing.expect(std.mem.indexOf(u8, manifest_source, "\"ready_next_gap\": \"phase14-workqueue-pending-bit-audit\"") == null);
    try expectContains(
        survey_source,
        "workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`, surveyed commit `9b98d3b9c812840bf279508030be0b8de093736c`, ready-next none currently recorded, blocked `phase14-workqueue-live-execution-blocker`",
    );
    try std.testing.expect(std.mem.indexOf(u8, survey_source, "phase14-workqueue-pending-bit-audit") == null);
}

test "phase14 workqueue traceability note keeps shared smoke metadata aligned" {
    const traceability_source = try readTraceabilitySource();
    defer std.testing.allocator.free(traceability_source);

    try expectContains(traceability_source, "lane key: `P14-L04`");
    try expectContains(traceability_source, "surveyed commit: `9b98d3b9c812840bf279508030be0b8de093736c`");
    try expectContains(traceability_source, "ready-next gap: none currently recorded");
    try expectContains(traceability_source, "blocked gap: `phase14-workqueue-live-execution-blocker`");
    try std.testing.expect(std.mem.indexOf(u8, traceability_source, "phase14-workqueue-pending-bit-audit") == null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_source, "lane key: `P14-L01`") == null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_source, "`007f00d0c6b6b430bfbb2110555544cc5faefe8b`") == null);
}
