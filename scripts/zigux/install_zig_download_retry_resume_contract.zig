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

fn requireOrderAfter(source: []const u8, anchor: []const u8, before: []const u8, after: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, source, anchor) orelse return error.MissingAnchorMarker;
    const before_offset = std.mem.indexOf(u8, source[anchor_index..], before) orelse return error.MissingBeforeMarker;
    const after_offset = std.mem.indexOf(u8, source[anchor_index..], after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_offset < after_offset);
}

test "curl download path keeps retry and resume flags" {
    try requireContains(install_zig_source, "def copy_url_to_file_with_curl(");
    try requireContains(install_zig_source, "'curl',");
    try requireContains(install_zig_source, "'--fail',");
    try requireContains(install_zig_source, "'--location',");
    try requireContains(install_zig_source, "'--retry',");
    try requireContains(install_zig_source, "'--retry-all-errors',");
    try requireContains(install_zig_source, "'--retry-delay',");
    try requireContains(install_zig_source, "'--connect-timeout',");
    try requireContains(install_zig_source, "'--speed-limit',");
    try requireContains(install_zig_source, "'--speed-time',");
    try requireContains(install_zig_source, "'--continue-at',\n        '-',");
    try requireOrder(
        install_zig_source,
        "destination.parent.mkdir(parents=True, exist_ok=True)",
        "subprocess.run(cmd, check=True)",
    );
}

test "urllib fallback resumes only after partial responses" {
    try requireContains(
        install_zig_source,
        "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:",
    );
    try requireContains(
        install_zig_source,
        "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})",
    );
    try requireContains(
        install_zig_source,
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
    );
    try requireContains(install_zig_source, "request = build_download_request(url, resume_offset)");
    try requireContains(install_zig_source, "append = resume_offset > 0 and status == 206");
    try requireContains(
        install_zig_source,
        "if not append and destination.exists():\n                    destination.unlink()",
    );
    try requireOrderAfter(
        install_zig_source,
        "def copy_url_to_file(",
        "if shutil.which('curl') is not None:",
        "for attempt in range(1, retries + 1):",
    );
}

test "failed curl cleanup stays before urllib fallback" {
    try requireContains(
        install_zig_source,
        "if destination.exists() and destination.stat().st_size == 0:\n                destination.unlink()",
    );
    try requireOrderAfter(
        install_zig_source,
        "def copy_url_to_file(",
        "except (FileNotFoundError, subprocess.CalledProcessError) as exc:",
        "for attempt in range(1, retries + 1):",
    );
    try requireOrderAfter(
        install_zig_source,
        "def copy_url_to_file(",
        "if destination.exists() and destination.stat().st_size == 0:",
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
    );
}

test "installer self-test covers resume and curl preference" {
    try requireContains(install_zig_source, "resume_headers: list[str | None] = []");
    try requireContains(install_zig_source, "assert range_header == 'bytes=4-'");
    try requireContains(install_zig_source, "assert temp_path.read_bytes() == b'zig-data'");
    try requireContains(install_zig_source, "assert resume_headers == [None, 'bytes=4-']");
    try requireContains(install_zig_source, "assert '--continue-at' in curl_commands[0]");
    try requireContains(install_zig_source, "curl_copy_calls: list[tuple[str, Path, int, float]] = []");
    try requireContains(install_zig_source, "assert curl_copy_calls == [");
}
