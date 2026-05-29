const std = @import("std");

const archive_stage_markers = [_][]const u8{
    "def stage_archive(local_archive: Path | None, tarball_url: str, archive_path: Path) -> str:",
    "if local_archive is not None:",
    "local Zig archive not found",
    "local Zig archive is not a regular file",
    "shutil.copyfile(local_archive, archive_path)",
    "return 'local_archive'",
    "copy_url_to_file(tarball_url, archive_path)",
    "return 'download'",
};

const archive_target_markers = [_][]const u8{
    "parser.add_argument('--archive'",
    "parser.add_argument('--archive-target'",
    "archive_target_key = args.archive_target or target_key",
    "archive_target_key != target_key",
    "load_policy_archive_sha256(TOOLCHAIN_POLICY, archive_target_key)",
    "no pinned archive sha256 for target {archive_target_key}",
    "ZIG_INSTALL_ARCHIVE_TARGET={archive_target_key}",
};

const archive_status_markers = [_][]const u8{
    "verify_archive_sha256(archive_path, expected_archive_sha256)",
    "ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}",
    "ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified",
    "ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified",
    "ZIG_INSTALL_SOURCE={archive_source}",
    "ZIG_INSTALL_STATUS=pass",
};

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(256 * 1024),
    );
}

fn expectAll(source: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try std.testing.expect(contains(source, marker));
    }
}

test "install-zig keeps local archive staging separate from network download staging" {
    const installer_source = try readRepoFile(std.testing.allocator, "scripts/zigux/install-zig.py");
    defer std.testing.allocator.free(installer_source);

    try expectAll(installer_source, &archive_stage_markers);
}

test "install-zig preserves archive-target override and pinned sha guardrails" {
    const installer_source = try readRepoFile(std.testing.allocator, "scripts/zigux/install-zig.py");
    defer std.testing.allocator.free(installer_source);

    try expectAll(installer_source, &archive_target_markers);
    try expectAll(installer_source, &archive_status_markers);
}

test "install-zig self-test names the archive staging success and failure cases" {
    const installer_source = try readRepoFile(std.testing.allocator, "scripts/zigux/install-zig.py");
    defer std.testing.allocator.free(installer_source);

    const self_test_markers = [_][]const u8{
        "zigux_install_zig_archive_stage_",
        "local_archive.write_bytes(b'local-zig-archive')",
        "assert source == 'local_archive'",
        "expected missing local archive to fail",
        "zigux_install_zig_download_stage_",
        "assert source == 'download'",
        "ZIG_INSTALL_SELF_TEST_CASE_COUNT=46",
    };

    try expectAll(installer_source, &self_test_markers);
}

test "pinned toolchain policy still declares the archive target consumed by installer staging" {
    const policy_source = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy_source);

    const policy_markers = [_][]const u8{
        "archive_sha256",
        "x86_64-linux",
        "0.17.0-dev.87+9b177a7d2",
        "phase2-toolchain",
        "phase2-validate",
    };

    try expectAll(policy_source, &policy_markers);
}
