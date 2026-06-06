const std = @import("std");

const installer_source = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "self-test route reports pass status and current case count" {
    try expectContains(installer_source, "parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')");
    try expectOrder(
        installer_source,
        "if args.self_test:\n        return run_self_test()",
        "policy_channel = load_policy_channel()",
    );
    try expectContains(installer_source, "def run_self_test() -> int:");
    try expectContains(installer_source, "print('ZIG_INSTALL_SELF_TEST=pass')");
    try expectContains(installer_source, "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=46')");
}

test "self-test covers target resolution and explicit-version offline fallback" {
    try expectContains(installer_source, "assert normalize_os('Linux') == 'linux'");
    try expectContains(installer_source, "assert normalize_arch('amd64') == 'x86_64'");
    try expectContains(installer_source, "assert resolve_target(sample_index, 'master', 'x86_64', 'linux') == (");
    try expectContains(installer_source, "assert resolve_target(sample_index, '0.17.0-dev.758+748e7c5e3', 'x86_64', 'linux') == (");
    try expectContains(installer_source, "globals()['read_index'] = lambda: (_ for _ in ()).throw(TimeoutError('timed out'))");
    try expectContains(installer_source, "assert load_index('0.17.0-dev.758+748e7c5e3') == {}");
    try expectContains(installer_source, "load_index('master')");
    try expectContains(installer_source, "raise AssertionError('expected non-explicit channel timeout to fail')");
}

test "self-test covers policy, digest, retry, and download action paths" {
    try expectContains(installer_source, "assert load_policy_archive_sha256(policy_path, 'x86_64-linux') is None");
    try expectContains(installer_source, "assert 'duplicate toolchain policy keys' in str(exc)");
    try expectContains(installer_source, "assert 'duplicate archive_sha256 targets' in str(exc)");
    try expectContains(installer_source, "assert verify_archive_sha256(archive_path, expected_sha256) == expected_sha256");
    try expectContains(installer_source, "assert 'zig archive sha256 mismatch' in str(exc)");
    try expectContains(installer_source, "assert parse_retry_after({'Retry-After': '7'}) == 7.0");
    try expectContains(installer_source, "assert retry_delay_seconds(1, default_delay=0.5, headers={'Retry-After': '60'}) == MAX_RETRY_DELAY");
    try expectContains(installer_source, "assert throttled_sleep_calls == [0.0]");
    try expectContains(installer_source, "assert throttled_download_attempts == 2");
    try expectContains(installer_source, "assert resume_headers == [None, 'bytes=4-']");
    try expectContains(installer_source, "assert curl_commands[0][0] == 'curl'");
    try expectContains(installer_source, "assert curl_copy_calls == [");
}

test "self-test covers layout, staging, and failure guards" {
    try expectContains(installer_source, "assert resolve_bin_dir(root_layout) == root_layout");
    try expectContains(installer_source, "assert resolve_bin_dir(bin_layout) == bin_layout / 'bin'");
    try expectContains(installer_source, "assert 'could not locate zig binary' in str(exc)");
    try expectContains(installer_source, "source = stage_archive(local_archive, 'https://example.invalid/archive.tar.xz', staged_archive)");
    try expectContains(installer_source, "assert source == 'local_archive'");
    try expectContains(installer_source, "assert 'local Zig archive not found' in str(exc)");
    try expectContains(installer_source, "source = stage_archive(None, 'https://example.invalid/archive.tar.xz', staged_archive)");
    try expectContains(installer_source, "assert source == 'download'");
    try expectContains(installer_source, "raise AssertionError('expected normalize_os to reject unsupported OS')");
    try expectContains(installer_source, "raise AssertionError('expected normalize_arch to reject unsupported architecture')");
    try expectContains(installer_source, "raise AssertionError('expected resolve_target to reject unknown channel')");
    try expectContains(installer_source, "raise AssertionError('expected resolve_target to reject unknown target')");
}
