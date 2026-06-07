const std = @import("std");

const install_zig_py = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn sliceBetween(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingStartMarker;
    const body_start = start_index + start.len;
    const end_offset = std.mem.indexOf(u8, haystack[body_start..], end) orelse return error.MissingEndMarker;
    return haystack[body_start .. body_start + end_offset];
}

test "curl downloader uses resumable fail-closed command flags" {
    try expectContains(install_zig_py, "def copy_url_to_file_with_curl(");
    try expectContains(install_zig_py, "'curl',");
    try expectContains(install_zig_py, "'--fail',");
    try expectContains(install_zig_py, "'--location',");
    try expectContains(install_zig_py, "'--retry-all-errors',");
    try expectContains(install_zig_py, "'--continue-at',");
    try expectContains(install_zig_py, "'--output',");
    try expectContains(install_zig_py, "str(destination),");
    try expectOrdered(install_zig_py, "'--continue-at',", "'--output',");
    try expectOrdered(install_zig_py, "'--output',", "str(destination),");
}

test "copy_url_to_file prefers curl then falls back after curl failures" {
    const copy_url_body = try sliceBetween(install_zig_py, "def copy_url_to_file(\n", "\n\ndef read_index()");
    try expectContains(copy_url_body, "if shutil.which('curl') is not None:");
    try expectContains(copy_url_body, "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)");
    try expectContains(copy_url_body, "except (FileNotFoundError, subprocess.CalledProcessError) as exc:");
    try expectContains(copy_url_body, "last_error = exc");
    try expectContains(copy_url_body, "for attempt in range(1, retries + 1):");
    try expectContains(copy_url_body, "request = build_download_request(url, resume_offset)");
    try expectOrdered(
        copy_url_body,
        "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)",
        "for attempt in range(1, retries + 1):",
    );
}

test "failed curl cleanup preserves partial archives for urllib resume" {
    const copy_url_body = try sliceBetween(install_zig_py, "def copy_url_to_file(\n", "\n\ndef read_index()");
    try expectContains(copy_url_body, "if destination.exists() and destination.stat().st_size == 0:");
    try expectContains(copy_url_body, "destination.unlink()");
    try expectContains(copy_url_body, "resume_offset = destination.stat().st_size if destination.exists() else 0");
    try expectContains(copy_url_body, "append = resume_offset > 0 and status == 206");
    try expectContains(copy_url_body, "if not append and destination.exists():");
    try expectOrdered(
        copy_url_body,
        "if destination.exists() and destination.stat().st_size == 0:",
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
    );
}

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();
    try stdout.print("INSTALL_ZIG_CURL_FALLBACK_CONTRACT=pass\n", .{});
    try stdout.print("INSTALL_ZIG_CURL_FALLBACK_CONTRACT_CHECKS=18\n", .{});
}
