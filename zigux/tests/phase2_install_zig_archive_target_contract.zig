const std = @import("std");

const max_file_bytes = 1024 * 1024;

const installer_archive_target_markers = [_][]const u8{
    "parser.add_argument('--archive-target'",
    "Archive target key from scripts/zigux/zig-toolchain-policy.json when using --archive.",
    "archive_target_key = args.archive_target or target_key",
    "if args.archive is not None and channel == policy_channel and archive_target_key != target_key:",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)",
    "if args.archive is not None and channel == policy_channel and expected_archive_sha256 is None:",
    "no pinned archive sha256 for target {archive_target_key}",
    "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')",
    "stage_archive(local_archive, tarball_url, archive_path)",
    "verify_archive_sha256(archive_path, expected_archive_sha256)",
};

const policy_archive_scope_markers = [_][]const u8{
    "\"channel\": \"0.17.0-dev.87+9b177a7d2\"",
    "\"archive_sha256\"",
    "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"",
    "\"archive_target_scope\"",
    "\"phase2-toolchain\"",
};

const workflow_archive_target_markers = [_][]const u8{
    "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
    "if len(targets) != 1:",
    "ZIGUX_ZIG_TARGET",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
};

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_file_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "install-zig keeps local archive target verification policy-bound" {
    const installer = try readRepoFileAlloc(std.testing.allocator, "scripts/zigux/install-zig.py");
    defer std.testing.allocator.free(installer);

    inline for (installer_archive_target_markers) |marker| {
        try expectContains(installer, marker);
    }

    try expectOrdered(installer, "archive_target_key = args.archive_target or target_key", "load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)");
    try expectOrdered(installer, "load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)", "no pinned archive sha256 for target {archive_target_key}");
    try expectOrdered(installer, "no pinned archive sha256 for target {archive_target_key}", "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')");
    try expectOrdered(installer, "print(f'ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}')", "stage_archive(local_archive, tarball_url, archive_path)");
    try expectOrdered(installer, "stage_archive(local_archive, tarball_url, archive_path)", "verify_archive_sha256(archive_path, expected_archive_sha256)");
}

test "policy exposes a single pinned archive target for the installer path" {
    const policy = try readRepoFileAlloc(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);

    inline for (policy_archive_scope_markers) |marker| {
        try expectContains(policy, marker);
    }

    try expectOrdered(policy, "\"archive_sha256\"", "\"archive_target_scope\"");
    try expectOrdered(policy, "\"archive_target_scope\"", "\"required_make_routes\"");
}

test "bootstrap workflow reuses the same archive target for local and downloaded archives" {
    const workflow = try readRepoFileAlloc(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    inline for (workflow_archive_target_markers) |marker| {
        try expectContains(workflow, marker);
    }

    try expectOrdered(workflow, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]", "ZIGUX_ZIG_TARGET");
    try expectOrdered(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"", "--archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectOrdered(workflow, "try_local_archive()", "try_download()");
    try expectOrdered(workflow, "try_download()", "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org");
}
