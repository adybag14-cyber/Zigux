const std = @import("std");

const install_zig_source = @embedFile("install-zig.py");

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrder(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn requireSequence(source: []const u8, needles: []const []const u8) !void {
    var offset: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, source[offset..], needle) orelse return error.MissingSequenceMarker;
        offset += relative + needle.len;
    }
}

test "install-zig curl path uses resilient transfer flags" {
    try requireContains(install_zig_source, "def copy_url_to_file_with_curl(");
    try requireContains(install_zig_source, "'curl',");
    try requireContains(install_zig_source, "'--fail',");
    try requireContains(install_zig_source, "'--location',");
    try requireContains(install_zig_source, "'--retry',");
    try requireContains(install_zig_source, "'--retry-all-errors',");
    try requireContains(install_zig_source, "'--continue-at',");
    try requireContains(install_zig_source, "'-',");
    try requireContains(install_zig_source, "'--output',");
}

test "curl is preferred but falls back to Python downloader" {
    try requireSequence(install_zig_source, &.{
        "def copy_url_to_file(",
        "if shutil.which('curl') is not None:",
        "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)",
        "except (FileNotFoundError, subprocess.CalledProcessError) as exc:",
        "last_error = exc",
        "for attempt in range(1, retries + 1):",
    });
}

test "failed empty curl download is removed before Python fallback" {
    try requireSequence(install_zig_source, &.{
        "except (FileNotFoundError, subprocess.CalledProcessError) as exc:",
        "last_error = exc",
        "if destination.exists() and destination.stat().st_size == 0:",
        "destination.unlink()",
        "for attempt in range(1, retries + 1):",
    });
}

test "installer self-test covers curl command and preference path" {
    try requireContains(install_zig_source, "copy_url_to_file_with_curl(");
    try requireContains(install_zig_source, "assert curl_commands[0][0] == 'curl'");
    try requireContains(install_zig_source, "assert '--continue-at' in curl_commands[0]");
    try requireContains(install_zig_source, "assert '--retry-all-errors' in curl_commands[0]");
    try requireContains(install_zig_source, "globals()['copy_url_to_file_with_curl'] = fake_curl_copy");
    try requireContains(install_zig_source, "assert curl_copy_calls ==");
}

test "installer download path uses the shared curl-aware copy helper" {
    try requireContains(install_zig_source, "copy_url_to_file(tarball_url, archive_path)");
    try requireOrder(
        install_zig_source,
        "def copy_url_to_file(",
        "copy_url_to_file(tarball_url, archive_path)",
    );
    try requireOrder(
        install_zig_source,
        "copy_url_to_file(tarball_url, archive_path)",
        "verify_archive_sha256(archive_path, expected_archive_sha256)",
    );
}
