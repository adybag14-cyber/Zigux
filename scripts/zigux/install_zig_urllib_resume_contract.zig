const std = @import("std");

const install_zig_source = @embedFile("install-zig.py");

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireBefore(source: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, source, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, source, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "urllib fallback builds range requests from the partial archive size" {
    try requireContains(
        install_zig_source,
        "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:",
    );
    try requireContains(
        install_zig_source,
        "if start_offset <= 0:\n        return url",
    );
    try requireContains(
        install_zig_source,
        "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})",
    );
    try requireContains(
        install_zig_source,
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
    );
    try requireContains(
        install_zig_source,
        "request = build_download_request(url, resume_offset)",
    );
    try requireBefore(
        install_zig_source,
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
        "request = build_download_request(url, resume_offset)",
    );
}

test "urllib fallback appends only when the server confirms partial content" {
    try requireContains(
        install_zig_source,
        "status = response_status(response)",
    );
    try requireContains(
        install_zig_source,
        "append = resume_offset > 0 and status == 206",
    );
    try requireContains(
        install_zig_source,
        "if not append and destination.exists():\n                    destination.unlink()",
    );
    try requireContains(
        install_zig_source,
        "copy_response_chunks(response, destination, append=append)",
    );
    try requireBefore(
        install_zig_source,
        "append = resume_offset > 0 and status == 206",
        "copy_response_chunks(response, destination, append=append)",
    );
}

test "urllib resume self-test covers timeout resume and restart behavior" {
    try requireContains(
        install_zig_source,
        "resume_headers: list[str | None] = []",
    );
    try requireContains(
        install_zig_source,
        "return FakeResponse([b'zig-', TimeoutError('timed out')], status=200)",
    );
    try requireContains(
        install_zig_source,
        "assert range_header == 'bytes=4-'",
    );
    try requireContains(
        install_zig_source,
        "return FakeResponse([b'data'], status=206)",
    );
    try requireContains(
        install_zig_source,
        "assert temp_path.read_bytes() == b'zig-data'",
    );
    try requireContains(
        install_zig_source,
        "assert resume_headers == [None, 'bytes=4-']",
    );
}
