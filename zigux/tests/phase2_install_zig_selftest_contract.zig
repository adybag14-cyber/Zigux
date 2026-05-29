const std = @import("std");

fn readInstallZig(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/install-zig.py",
        allocator,
        .limited(96 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var offset: usize = 0;
    for (markers) |marker| {
        const relative_index = std.mem.indexOf(u8, haystack[offset..], marker) orelse return error.MarkerOutOfOrder;
        offset += relative_index + marker.len;
    }
}

test "install-zig self-test keeps current action-path coverage visible" {
    const install_zig = try readInstallZig(std.testing.allocator);
    defer std.testing.allocator.free(install_zig);

    try expectContains(install_zig, "parser.add_argument('--self-test'");
    try expectContains(install_zig, "if args.self_test:");
    try expectContains(install_zig, "return run_self_test()");
    try expectContains(install_zig, "print('ZIG_INSTALL_SELF_TEST=pass')");
    try expectContains(install_zig, "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')");

    try expectOrdered(install_zig, &.{
        "def run_self_test() -> int:",
        "assert normalize_os('Linux') == 'linux'",
        "assert normalize_arch('amd64') == 'x86_64'",
        "assert resolve_target(sample_index, 'master', 'x86_64', 'linux')",
        "assert load_index('0.17.0-dev.87+9b177a7d2') == {}",
        "assert load_policy_channel(policy_path, '0.15.0') == '0.17.0-dev.87+9b177a7d2'",
        "assert verify_archive_sha256(archive_path, expected_sha256) == expected_sha256",
        "assert retry_delay_seconds(1, default_delay=0.5, headers={'Retry-After': '60'}) == MAX_RETRY_DELAY",
        "def resumable_open_url(target: str | urllib.request.Request",
        "assert temp_path.read_bytes() == b'zig-data'",
        "def throttled_download_open_url(target: str | urllib.request.Request",
        "assert throttled_download_attempts == 2",
        "copy_url_to_file_with_curl(",
        "assert '--continue-at' in curl_commands[0]",
        "assert curl_copy_calls == [",
        "source = stage_archive(local_archive, 'https://example.invalid/archive.tar.xz', staged_archive)",
        "assert source == 'local_archive'",
        "source = stage_archive(None, 'https://example.invalid/archive.tar.xz', staged_archive)",
        "assert source == 'download'",
        "print('ZIG_INSTALL_SELF_TEST=pass')",
        "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')",
    });
}

test "install-zig self-test remains local and download-free" {
    const install_zig = try readInstallZig(std.testing.allocator);
    defer std.testing.allocator.free(install_zig);

    try expectOrdered(install_zig, &.{
        "if args.self_test:",
        "return run_self_test()",
        "policy_channel = load_policy_channel()",
        "index = load_index(channel)",
        "archive_source = stage_archive(local_archive, tarball_url, archive_path)",
    });
}
