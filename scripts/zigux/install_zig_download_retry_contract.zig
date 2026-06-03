const std = @import("std");
const testing = std.testing;

const installer_source = @embedFile("install-zig.py");

fn requireMarker(marker: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, installer_source, marker) != null);
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, installer_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, installer_source, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "install zig curl downloader remains resumable and retry hardened" {
    try requireMarker("def copy_url_to_file_with_curl(");
    try requireMarker("'curl'");
    try requireMarker("'--fail'");
    try requireMarker("'--location'");
    try requireMarker("'--retry-all-errors'");
    try requireMarker("'--continue-at'");
    try requireMarker("'-'");
    try requireMarker("'--speed-limit'");
    try requireMarker("'--speed-time'");
    try requireMarker("'--output'");
    try requireMarker("str(destination)");
    try requireMarker("subprocess.run(cmd, check=True)");

    try requireOrdered("def copy_url_to_file_with_curl(", "subprocess.run(cmd, check=True)");
    try requireOrdered("'--continue-at'", "'-'");
    try requireOrdered("'--output'", "str(destination)");
}

test "install zig urllib fallback keeps range resume semantics" {
    try requireMarker("def build_download_request(url: str, start_offset: int)");
    try requireMarker("headers={'Range': f'bytes={start_offset}-'}");
    try requireMarker("resume_offset = destination.stat().st_size if destination.exists() else 0");
    try requireMarker("request = build_download_request(url, resume_offset)");
    try requireMarker("append = resume_offset > 0 and status == 206");
    try requireMarker("if not append and destination.exists():");
    try requireMarker("destination.unlink()");
    try requireMarker("copy_response_chunks(response, destination, append=append)");

    try requireOrdered("resume_offset = destination.stat().st_size if destination.exists() else 0", "request = build_download_request(url, resume_offset)");
    try requireOrdered("request = build_download_request(url, resume_offset)", "copy_response_chunks(response, destination, append=append)");
}

test "install zig retry after and archive stage delegation stay guarded" {
    try requireMarker("RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}");
    try requireMarker("def parse_retry_after(headers)");
    try requireMarker("def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None)");
    try requireMarker("parsed_retry_after = parse_retry_after(headers)");
    try requireMarker("return min(parsed_retry_after, MAX_RETRY_DELAY)");
    try requireMarker("copy_url_to_file(tarball_url, archive_path)");
    try requireMarker("return 'download'");
    try requireMarker("return 'local_archive'");

    try requireOrdered("def stage_archive(local_archive: Path | None, tarball_url: str, archive_path: Path)", "copy_url_to_file(tarball_url, archive_path)");
    try requireOrdered("copy_url_to_file(tarball_url, archive_path)", "return 'download'");
}

test "install zig self test still exercises download retry surface" {
    try requireMarker("throttled_urlopen");
    try requireMarker("raise urllib.error.HTTPError(");
    try requireMarker("code=429");
    try requireMarker("resume_headers == [None, 'bytes=4-']");
    try requireMarker("curl_commands[0][0] == 'curl'");
    try requireMarker("'--retry-all-errors' in curl_commands[0]");
    try requireMarker("'--continue-at' in curl_commands[0]");
    try requireMarker("ZIG_INSTALL_SELF_TEST_CASE_COUNT=46");
}
