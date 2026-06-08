const std = @import("std");

const installer_source = @embedFile("install-zig.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn requireOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse {
        std.debug.print("missing first marker: {s}\n", .{first});
        return error.MissingMarker;
    };
    const second_index = std.mem.indexOf(u8, haystack, second) orelse {
        std.debug.print("missing second marker: {s}\n", .{second});
        return error.MissingMarker;
    };
    try std.testing.expect(first_index < second_index);
}

fn curlCommandBlock(source: []const u8) ![]const u8 {
    const start_marker =
        \\def copy_url_to_file_with_curl(
    ;
    const start = std.mem.indexOf(u8, source, start_marker) orelse return error.MissingCurlCommand;
    const tail = source[start..];
    const end_marker =
        \\def copy_url_to_file(
    ;
    const end = std.mem.indexOf(u8, tail, end_marker) orelse return error.MissingCurlCommand;
    return tail[0..end];
}

test "curl diagnostic flags stay paired before retry and resume flags" {
    const block = try curlCommandBlock(installer_source);

    try requireContains(block, "'--silent'");
    try requireContains(block, "'--show-error'");
    try requireOrder(block, "'--silent'", "'--show-error'");
    try requireOrder(block, "'--show-error'", "'--retry'");
    try requireOrder(block, "'--retry-all-errors'", "'--continue-at'");
    try requireOrder(block, "'--continue-at'", "'--output'");
}

test "curl path remains preferred before urllib fallback loop" {
    try requireOrder(
        installer_source,
        "if shutil.which('curl') is not None:",
        "for attempt in range(1, retries + 1):",
    );
    try requireOrder(
        installer_source,
        "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)",
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
    );
}

test "zero-byte curl failures are still cleaned before fallback resume" {
    try requireOrder(
        installer_source,
        "except (FileNotFoundError, subprocess.CalledProcessError) as exc:",
        "if destination.exists() and destination.stat().st_size == 0:",
    );
    try requireOrder(
        installer_source,
        "destination.unlink()",
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
    );
}
