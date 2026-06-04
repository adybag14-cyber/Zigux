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
    try requireOrder(source[anchor_index..], before, after);
}

test "installer curl path keeps resumable retry flags" {
    try requireContains(
        install_zig_source,
        "def copy_url_to_file_with_curl(",
    );
    try requireContains(
        install_zig_source,
        "'--retry-all-errors',",
    );
    try requireContains(
        install_zig_source,
        "'--continue-at',\n        '-',",
    );
    try requireOrder(
        install_zig_source,
        "'--retry',",
        "'--retry-all-errors',",
    );
    try requireOrder(
        install_zig_source,
        "'--continue-at',",
        "'--output',",
    );
}

test "copy_url_to_file prefers curl before urllib fallback" {
    try requireContains(
        install_zig_source,
        "if shutil.which('curl') is not None:",
    );
    try requireContains(
        install_zig_source,
        "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)",
    );
    try requireContains(
        install_zig_source,
        "except (FileNotFoundError, subprocess.CalledProcessError) as exc:",
    );
    try requireContains(
        install_zig_source,
        "if destination.exists() and destination.stat().st_size == 0:\n                destination.unlink()",
    );
    try requireOrderAfter(
        install_zig_source,
        "def copy_url_to_file(",
        "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)",
        "for attempt in range(1, retries + 1):",
    );
}

test "urllib fallback resumes partial archives only after partial content" {
    try requireContains(
        install_zig_source,
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
    );
    try requireContains(
        install_zig_source,
        "request = build_download_request(url, resume_offset)",
    );
    try requireContains(
        install_zig_source,
        "append = resume_offset > 0 and status == 206",
    );
    try requireContains(
        install_zig_source,
        "if not append and destination.exists():\n                    destination.unlink()",
    );
    try requireOrder(
        install_zig_source,
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
        "request = build_download_request(url, resume_offset)",
    );
    try requireOrder(
        install_zig_source,
        "append = resume_offset > 0 and status == 206",
        "copy_response_chunks(response, destination, append=append)",
    );
}

test "staging downloads through resumable copy helper" {
    if (std.mem.indexOf(u8, install_zig_source, "def stage_archive(") != null) {
        try requireContains(
            install_zig_source,
            "copy_url_to_file(tarball_url, archive_path)",
        );
        try requireContains(
            install_zig_source,
            "return 'download'",
        );
        try requireOrder(
            install_zig_source,
            "archive_source = stage_archive(local_archive, tarball_url, archive_path)",
            "verify_archive_sha256(archive_path, expected_archive_sha256)",
        );
    } else {
        try requireOrder(
            install_zig_source,
            "copy_url_to_file(tarball_url, archive_path)",
            "verify_archive_sha256(archive_path, expected_archive_sha256)",
        );
    }
}
