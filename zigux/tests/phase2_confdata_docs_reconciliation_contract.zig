const std = @import("std");

const ConfdataManifest = struct {
    tool: []const u8,
    status: []const u8,
    case_count: usize,
    cases: []const []const u8,
    helper_local_anchors: []const []const u8,
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(128 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "confdata manifest records the current shared fixture and helper-local packet" {
    const manifest_json = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(ConfdataManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("scripts/zigux/kconfig/confdata_bridge.zig", manifest.tool);
    try std.testing.expectEqualStrings("closed", manifest.status);
    try std.testing.expectEqual(@as(usize, 16), manifest.case_count);
    try std.testing.expectEqual(@as(usize, 16), manifest.cases.len);
    try std.testing.expectEqual(@as(usize, 36), manifest.helper_local_anchors.len);
    try std.testing.expectEqualStrings("explicit_empty_assignments", manifest.cases[15]);

    var found_output_mode = false;
    var found_large_reader = false;
    var found_alloc_failure = false;
    for (manifest.helper_local_anchors) |anchor| {
        if (std.mem.eql(u8, anchor, "confdata bridge emits auto.conf output through the explicit mode surface")) {
            found_output_mode = true;
        }
        if (std.mem.eql(u8, anchor, "confdata bridge file reader accepts config inputs beyond one mebibyte")) {
            found_large_reader = true;
        }
        if (std.mem.eql(u8, anchor, "confdata bridge preserves duplicate unset ownership on allocation failure")) {
            found_alloc_failure = true;
        }
    }

    try std.testing.expect(found_output_mode);
    try std.testing.expect(found_large_reader);
    try std.testing.expect(found_alloc_failure);
}

test "confdata documentation points at shipped current-master checkers only" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-confdata-bridge-survey.md");
    defer std.testing.allocator.free(survey);
    const next_step = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-confdata-bridge-next-step-note.md");
    defer std.testing.allocator.free(next_step);

    try expectContains(survey, "`16` `confdata_cases`");

    for ([_][]const u8{ survey, next_step }) |doc| {
        try expectContains(doc, "`16`-case confdata packet");
        try expectContains(doc, "`36`-anchor helper-local bridge packet");
        try expectContains(doc, "`python3 scripts/zigux/check-kconfig-bridge.py --self-test`");
        try expectContains(doc, "`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`");
        try expectAbsent(doc, "check-phase2-confdata-helper-anchor-alignment.py");
        try expectAbsent(doc, "`15`-case confdata packet");
        try expectAbsent(doc, "`27`-anchor helper-local bridge packet");
    }
}

test "confdata case roster in docs mirrors the manifest tail" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-confdata-bridge-survey.md");
    defer std.testing.allocator.free(survey);
    const manifest_json = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(ConfdataManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    for (parsed.value.cases[12..]) |case_name| {
        try expectContains(survey, case_name);
    }

    try expectContains(survey, "explicit output-mode");
    try expectContains(survey, "large-file-reader");
    try expectContains(survey, "allocation-failure ownership proofs");
}
