const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-toolchain-pinning.py";

fn readChecker(allocator: std.mem.Allocator) ![]const u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        checker_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "toolchain pinning checker keeps the pinned archive identity exact" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "ARCHIVE_TARGET = \"x86_64-linux\"");
    try expectContains(checker, "ARCHIVE_CHANNEL = \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(checker, "ARCHIVE_SIZE = 58_159_088");
    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 51");
}

test "toolchain pinning checker names the required action-path surfaces" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "scripts/zigux/check-zig-toolchain.py");
    try expectContains(checker, "scripts/zigux/zig-toolchain-policy.json");
    try expectContains(checker, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(checker, "scripts/zigux/install-zig.py");
    try expectContains(checker, "scripts/zigux/check-phase2-toolchain-pin-scope.py");
    try expectContains(checker, "scripts/zigux/check-phase2-required-make-routes.py");
    try expectContains(checker, "scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
    try expectContains(checker, "zigux/tests/fixtures/phase2_tool_manifest.json");
}

test "toolchain pinning checker protects the local archive and mirror fallback route" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(checker, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(checker, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(checker, "curl -L --fail https://ziglang.org/download/community-mirrors.txt");
    try expectContains(checker, "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org");
}

test "toolchain pinning checker keeps its public pass sentinels" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_TOOLCHAIN_PINNING_MANIFEST_SYNC=pass");
    try expectContains(checker, "PHASE2_TOOLCHAIN_PINNING=pass");
    try expectContains(checker, "PHASE2_TOOLCHAIN_PINNING_ARCHIVE_README_MARKER_COUNT=10");
}
