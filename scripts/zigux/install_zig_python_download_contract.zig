const std = @import("std");

const installer_path = "scripts/zigux/install-zig.py";

fn readInstallerSource() ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        installer_path,
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectOrdered(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectOrderedAfter(source: []const u8, anchor: []const u8, later: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, source, anchor) orelse return error.MissingAnchorMarker;
    const later_index = std.mem.indexOfPos(u8, source, anchor_index + anchor.len, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(anchor_index < later_index);
}

test "installer keeps urllib fallback when curl is unavailable" {
    const source = try readInstallerSource();
    defer std.testing.allocator.free(source);

    try expectContains(source, "def copy_url_to_file(");
    try expectContains(source, "if shutil.which('curl') is not None:");
    try expectContains(source, "except (FileNotFoundError, subprocess.CalledProcessError) as exc:");
    try expectContains(source, "resume_offset = destination.stat().st_size if destination.exists() else 0");
    try expectContains(source, "request = build_download_request(url, resume_offset)");
    try expectContains(source, "append = resume_offset > 0 and status == 206");
    try expectContains(source, "copy_response_chunks(response, destination, append=append)");

    try expectOrderedAfter(
        source,
        "def copy_url_to_file(",
        "for attempt in range(1, retries + 1):",
    );
    try expectOrdered(
        source,
        "request = build_download_request(url, resume_offset)",
        "copy_response_chunks(response, destination, append=append)",
    );
}

test "installer self-test exercises no-curl resume and retry fallback paths" {
    const source = try readInstallerSource();
    defer std.testing.allocator.free(source);

    try expectContains(source, "shutil.which = lambda name: None if name == 'curl' else original_which(name)");
    try expectContains(source, "resume_headers: list[str | None] = []");
    try expectContains(source, "assert range_header == 'bytes=4-'");
    try expectContains(source, "copy_url_to_file('https://example.invalid/archive.tar.xz', temp_path, retries=2, timeout=1.0)");
    try expectContains(source, "assert temp_path.read_bytes() == b'zig-data'");
    try expectContains(source, "RETRYABLE_HTTP_STATUS_CODES = {");
    try expectContains(source, "except urllib.error.HTTPError as exc:");
    try expectContains(source, "if exc.code not in RETRYABLE_HTTP_STATUS_CODES or attempt == retries:");
    try expectContains(source, "time.sleep(");
    try expectContains(source, "ZIG_INSTALL_SELF_TEST_CASE_COUNT=");

    try expectOrdered(
        source,
        "resume_headers: list[str | None] = []",
        "assert resume_headers == [None, 'bytes=4-']",
    );
}

test "installer still prefers curl but keeps the Python fallback reachable" {
    const source = try readInstallerSource();
    defer std.testing.allocator.free(source);

    try expectContains(source, "def copy_url_to_file_with_curl(");
    try expectContains(source, "'--continue-at',");
    try expectContains(source, "'--retry-all-errors',");
    try expectContains(source, "curl_copy_calls: list[tuple[str, Path, int, float]] = []");
    try expectContains(source, "Path('/tmp/zigux-install-zig-curl-preferred/archive.tar.xz')");
    try expectContains(source, "globals()['copy_url_to_file_with_curl'] = fake_curl_copy");

    try expectOrdered(
        source,
        "def copy_url_to_file_with_curl(",
        "def copy_url_to_file(",
    );
    try expectOrdered(
        source,
        "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)",
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
    );
}
