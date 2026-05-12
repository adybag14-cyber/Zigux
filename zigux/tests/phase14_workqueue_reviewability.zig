const std = @import("std");

const manifest_source = @embedFile("phase14_end_to_end_smoke_manifest.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRootFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn readSurveySource() ![]u8 {
    return readRootFile("Documentation/zigux/phase14-end-to-end-smoke-survey.md", 64 * 1024);
}

fn readTraceabilitySource() ![]u8 {
    return readRootFile("Documentation/zigux/phase14-core-boundary-traceability.md", 64 * 1024);
}

fn readWorkqueueManifestSource() ![]u8 {
    return readRootFile("zigux/tests/phase14_workqueue_bridge_manifest.json", 64 * 1024);
}

fn readWorkqueueSurveySource() ![]u8 {
    return readRootFile("Documentation/zigux/phase14-workqueue-bridge-survey.md", 64 * 1024);
}

test "phase14 shared smoke manifest keeps workqueue reviewability explicit" {
    try expectContains(manifest_source, "\"zigux/tests/phase14_workqueue_reviewability.zig\"");
    try expectContains(manifest_source, "\"label\": \"phase14-workqueue-reviewability-tests\"");
    try expectContains(manifest_source, "\"root_source\": \"phase14_workqueue_reviewability.zig\"");
    try expectContains(manifest_source, "\"coverage\": \"full_bundle_only\"");
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
        "workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`, surveyed commit `9b98d3b9c812840bf279508030be0b8de093736c`, ready-next `none currently recorded`, blocked `phase14-workqueue-live-execution-blocker`",
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

test "phase14 workqueue anchor packet keeps the delayed-work governance follow-through explicit" {
    const workqueue_manifest_source = try readWorkqueueManifestSource();
    defer std.testing.allocator.free(workqueue_manifest_source);

    const workqueue_survey_source = try readWorkqueueSurveySource();
    defer std.testing.allocator.free(workqueue_survey_source);

    try expectContains(workqueue_manifest_source, "\"lane_key\": \"P14-L04\"");
    try expectContains(workqueue_manifest_source, "\"surveyed_commit\": \"9b98d3b9c812840bf279508030be0b8de093736c\"");
    try expectContains(workqueue_manifest_source, "\"id\": \"phase14-workqueue-delayed-requeue-governance\"");
    try expectContains(workqueue_manifest_source, "\"id\": \"phase14-workqueue-flush-drain-governance\"");
    try expectContains(workqueue_manifest_source, "\"id\": \"phase14-workqueue-rescuer-mayday-governance\"");
    try expectContains(workqueue_manifest_source, "\"id\": \"phase14-workqueue-live-execution-blocker\"");
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, workqueue_manifest_source, "\"status\": \"blocked_on_live_concurrency\""));
    try std.testing.expect(std.mem.count(u8, workqueue_manifest_source, "\"status\": \"starter_landed\"") >= 16);

    try expectContains(workqueue_survey_source, "PHASE14_STATUS=blocked_maintenance");
    try expectContains(workqueue_survey_source, "phase14-workqueue-delayed-requeue-governance");
    try expectContains(workqueue_survey_source, "phase14-workqueue-flush-drain-governance");
    try expectContains(workqueue_survey_source, "phase14-workqueue-rescuer-mayday-governance");
    try expectContains(workqueue_survey_source, "delayed-work requeue control");
    try expectContains(workqueue_survey_source, "runtime `max_active` retuning ownership");
}
