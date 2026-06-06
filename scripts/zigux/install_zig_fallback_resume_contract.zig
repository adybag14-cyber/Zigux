const std = @import("std");

const install_zig_text = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "fallback downloader builds Range requests from existing partial archives" {
    try expectContains(install_zig_text, "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:");
    try expectContains(install_zig_text, "if start_offset <= 0:");
    try expectContains(install_zig_text, "return url");
    try expectContains(install_zig_text, "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})");
    try expectContains(install_zig_text, "resume_offset = destination.stat().st_size if destination.exists() else 0");
    try expectContains(install_zig_text, "request = build_download_request(url, resume_offset)");
    try expectBefore(
        install_zig_text,
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
        "request = build_download_request(url, resume_offset)",
    );
}

test "fallback downloader appends only after partial-content responses" {
    try expectContains(install_zig_text, "def response_status(response) -> int | None:");
    try expectContains(install_zig_text, "status = getattr(response, 'status', None)");
    try expectContains(install_zig_text, "if hasattr(response, 'getcode'):");
    try expectContains(install_zig_text, "return response.getcode()");
    try expectContains(install_zig_text, "status = response_status(response)");
    try expectContains(install_zig_text, "append = resume_offset > 0 and status == 206");
    try expectContains(install_zig_text, "copy_response_chunks(response, destination, append=append)");
    try expectBefore(install_zig_text, "status = response_status(response)", "append = resume_offset > 0 and status == 206");
    try expectBefore(install_zig_text, "append = resume_offset > 0 and status == 206", "copy_response_chunks(response, destination, append=append)");
}

test "fallback downloader replaces stale partial archives on full responses" {
    try expectContains(install_zig_text, "def copy_response_chunks(response, destination: Path, *, append: bool) -> None:");
    try expectContains(install_zig_text, "mode = 'ab' if append else 'wb'");
    try expectContains(install_zig_text, "if not append and destination.exists():");
    try expectContains(install_zig_text, "destination.unlink()");
    try expectBefore(install_zig_text, "destination.unlink()", "copy_response_chunks(response, destination, append=append)");
}
