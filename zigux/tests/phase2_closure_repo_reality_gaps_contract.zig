const std = @import("std");

const ContractFile = struct {
    contents: []u8,
};

const request_plan_allconfig_modes = [_][]const u8{
    "\"mode\": \"allmodconfig\"",
    "\"mode\": \"alldefconfig\"",
    "\"mode\": \"randconfig\"",
};

const sentinel_modes = [_][]const u8{
    "\"mode\": \"allnoconfig\"",
    "\"mode\": \"allyesconfig\"",
};

fn readFile(path: []const u8, limit: usize) !ContractFile {
    return .{
        .contents = try std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            std.testing.allocator,
            .limited(limit),
        ),
    };
}

fn unloadFile(file: ContractFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn expectAllconfigKeyCount(cases: []const u8, expected: usize) !void {
    var count: usize = 0;
    var cursor: []const u8 = cases;
    while (std.mem.indexOf(u8, cursor, "\"allconfig\"")) |index| {
        count += 1;
        cursor = cursor[index + "\"allconfig\"".len ..];
    }
    try std.testing.expectEqual(expected, count);
}

test "closure note keeps repo reality gaps parked after shared replay routes" {
    const closure = try readFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer unloadFile(closure);

    try expectContains(closure.contents, "## Repo-Reality Gaps");
    try expectContains(closure.contents, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
    try expectContains(closure.contents, "current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`");
    try expectContains(closure.contents, "fixture-backed rather than same-tree differential");
    try expectContains(closure.contents, "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`");
    try expectContains(closure.contents, "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`");
    try expectContains(closure.contents, "helper-local explicit-override roster remains broader by design");
    try expectOrdered(closure.contents, "## Shared Replay Routes", "## Repo-Reality Gaps");
    try expectOrdered(closure.contents, "## Repo-Reality Gaps", "## Next Step");
}

test "kconfig manifests preserve request plan, sentinel, and helper-local split" {
    const cases = try readFile("zigux/tests/fixtures/kconfig_bridge/cases.json", 256 * 1024);
    defer unloadFile(cases);
    const manifest = try readFile("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json", 256 * 1024);
    defer unloadFile(manifest);

    try expectAllconfigKeyCount(cases.contents, 3);
    inline for (request_plan_allconfig_modes) |mode| {
        try expectContains(cases.contents, mode);
    }
    inline for (sentinel_modes) |mode| {
        try expectContains(cases.contents, mode);
    }

    try expectContains(manifest.contents, "\"case_count\": 16");
    try expectContains(manifest.contents, "\"allconfig_sentinel_packet\"");
    try expectContains(manifest.contents, "\"allnoconfig_expected.json\"");
    try expectContains(manifest.contents, "\"allyesconfig_expected.json\"");
    try expectContains(manifest.contents, "\"allconfig_override_packet\"");
    try expectContains(manifest.contents, "\"allmodconfig_expected.json\"");
    try expectContains(manifest.contents, "\"alldefconfig_expected.json\"");
    try expectContains(manifest.contents, "\"randconfig_expected.json\"");
    try expectContains(manifest.contents, "\"helper_local_allconfig_explicit_override_modes\"");
    try expectContains(manifest.contents, "\"allnoconfig\"");
    try expectContains(manifest.contents, "\"allyesconfig\"");
}

test "companion Phase 2 surfaces keep the gap packet explicit without manifest gaps" {
    const tool_manifest = try readFile("zigux/tests/fixtures/phase2_tool_manifest.json", 512 * 1024);
    defer unloadFile(tool_manifest);
    const scripts_readme = try readFile("scripts/zigux/README.md", 256 * 1024);
    defer unloadFile(scripts_readme);
    const tests_readme = try readFile("zigux/tests/README.md", 256 * 1024);
    defer unloadFile(tests_readme);

    try expectContains(tool_manifest.contents, "\"repo_reality_gaps\": []");
    try expectContains(tool_manifest.contents, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try expectContains(tool_manifest.contents, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    try expectContains(tool_manifest.contents, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
    try expectNotContains(tool_manifest.contents, "scripts/kconfig/conf.c");
    try expectNotContains(tool_manifest.contents, "scripts/kconfig/confdata.c");

    try expectContains(scripts_readme.contents, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try expectContains(scripts_readme.contents, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectContains(scripts_readme.contents, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(scripts_readme.contents, "make -C zigux phase2-kconfig");

    try expectContains(tests_readme.contents, "zigux/tests/fixtures/kconfig_bridge/cases.json");
    try expectContains(tests_readme.contents, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    try expectContains(tests_readme.contents, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
    try expectContains(tests_readme.contents, "make -C zigux phase2-kconfig");
}
