const std = @import("std");

const testing = std.testing;
const installer = @embedFile("install-zig.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "install-zig keeps curl as the resumable first download path" {
    try expectContains(installer, "def copy_url_to_file_with_curl(");
    try expectContains(installer, "shutil.which('curl') is not None");
    try expectContains(installer, "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)");
    try expectContains(installer, "'--continue-at'");
    try expectContains(installer, "'--retry-all-errors'");
    try expectContains(installer, "'--speed-limit'");
    try expectContains(installer, "'--speed-time'");
}

test "install-zig python fallback resumes partial archives only on 206" {
    try expectContains(installer, "resume_offset = destination.stat().st_size if destination.exists() else 0");
    try expectContains(installer, "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})");
    try expectContains(installer, "append = resume_offset > 0 and status == 206");
    try expectContains(installer, "if not append and destination.exists():");
    try expectContains(installer, "destination.unlink()");
    try expectContains(installer, "copy_response_chunks(response, destination, append=append)");
}

test "install-zig fallback retries transient archive failures" {
    try expectContains(installer, "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}");
    try expectContains(installer, "DOWNLOAD_RETRIES = 4");
    try expectContains(installer, "DOWNLOAD_TIMEOUT = 120.0");
    try expectContains(installer, "parse_retry_after(headers)");
    try expectContains(installer, "except TimeoutError as exc:");
    try expectContains(installer, "except urllib.error.HTTPError as exc:");
    try expectContains(installer, "retry_delay_seconds(");
}

test "install-zig self-test covers resume and curl command markers" {
    try expectContains(installer, "resume_headers == [None, 'bytes=4-']");
    try expectContains(installer, "assert temp_path.read_bytes() == b'zig-data'");
    try expectContains(installer, "assert '--continue-at' in curl_commands[0]");
    try expectContains(installer, "assert '--retry-all-errors' in curl_commands[0]");
    try expectContains(installer, "curl_copy_calls == [");
    try expectContains(installer, "ZIG_INSTALL_SELF_TEST=pass");
}
