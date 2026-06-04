const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

test "phase2 tests readme keeps local archive reminder packet explicit" {
    const tests_readme = try readRepoFile("zigux/tests/README.md", 128 * 1024);
    defer std.testing.allocator.free(tests_readme);

    try expectContains(tests_readme, "current `master` now directly materializes `third_party/README.md`");
    try expectContains(tests_readme, "scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectContains(tests_readme, "scripts/zigux/check-lane05-local-archive-readme.py");
    try expectContains(tests_readme, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
    try expectContains(tests_readme, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz --archive-target x86_64-linux");
    try expectContains(tests_readme, "local-first `third_party`, canonical `adybag14-cyber/zig` release, mirror, then direct-download bootstrap order");
    try expectContains(tests_readme, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try expectContains(tests_readme, "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test");

    try expectOrder(
        tests_readme,
        "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz",
        "local-first `third_party`, canonical `adybag14-cyber/zig` release, mirror, then direct-download bootstrap order",
    );
}

test "third party archive readme keeps pinned archive and staged helper surfaces aligned" {
    const archive_readme = try readRepoFile("third_party/README.md", 32 * 1024);
    defer std.testing.allocator.free(archive_readme);

    try expectContains(archive_readme, "Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz`");
    try expectContains(archive_readme, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz.parts");
    try expectContains(archive_readme, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(archive_readme, "canonical `adybag14-cyber/zig` release before `community-mirrors.txt`");
    try expectContains(archive_readme, "direct `ziglang.org` download URL");
    try expectContains(archive_readme, "scripts/zigux/check-lane05-install-zig-archive-verification.py");
    try expectContains(archive_readme, "scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectContains(archive_readme, "scripts/zigux/check-lane05-stage-helper-selftest.py");

    try expectOrder(
        archive_readme,
        "Lane 05 bootstrap first reuses",
        "If the exact archive file is absent but",
    );
    try expectContains(archive_readme, "falls back to the canonical `adybag14-cyber/zig` release before `community-mirrors.txt` and the direct `ziglang.org` download URL");
}

test "lane05 archive checkers expose the guarded local first replay commands" {
    const workflow_checker = try readRepoFile("scripts/zigux/check-lane05-local-first-archive-workflow.py", 128 * 1024);
    defer std.testing.allocator.free(workflow_checker);

    const readme_checker = try readRepoFile("scripts/zigux/check-lane05-local-archive-readme.py", 64 * 1024);
    defer std.testing.allocator.free(readme_checker);

    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 128 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    try expectContains(workflow_checker, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow_checker, "--parts-dir \"$repo_archive_parts_dir\"");
    try expectContains(workflow_checker, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow_checker, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try expectContains(workflow_checker, "if try_download \"$ZIGUX_ZIG_URL\"; then");

    try expectContains(readme_checker, "expected exactly one archive target");
    try expectContains(readme_checker, "duplicate-suffix archive copies");
    try expectContains(readme_checker, "LANE05_LOCAL_ARCHIVE_README_MARKER_COUNT");
    try expectContains(readme_checker, "zig-x86_64-linux-0.17.0-dev.758+748e7c5e3 (1).tar.xz");

    try expectContains(scripts_readme, "third_party/README.md");
    try expectContains(scripts_readme, "scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(scripts_readme, "scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectContains(scripts_readme, "scripts/zigux/check-lane05-stage-helper-selftest.py");
}
