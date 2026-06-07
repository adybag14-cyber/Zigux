const std = @import("std");

const install_zig_source = @embedFile("install-zig.py");
const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requireAfter(haystack: []const u8, anchor: []const u8, needle: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, haystack, anchor) orelse return error.MissingAnchorMarker;
    const after_anchor = haystack[anchor_index + anchor.len ..];
    try requireContains(after_anchor, needle);
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
    const rest_start = first + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, haystack[rest_start..], needle) == null);
}

test "install-zig keeps curl as the resumable preferred action path" {
    try requireContains(install_zig_source, "def copy_url_to_file_with_curl(");
    try requireContains(install_zig_source, "if shutil.which('curl') is not None:");
    try requireOrder(
        install_zig_source,
        "if shutil.which('curl') is not None:",
        "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)",
    );
    try requireAfter(
        install_zig_source,
        "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)",
        "return",
    );
    try requireContains(install_zig_source, "'curl'");
    try requireContains(install_zig_source, "'--fail'");
    try requireContains(install_zig_source, "'--location'");
    try requireContains(install_zig_source, "'--retry'");
    try requireContains(install_zig_source, "'--retry-all-errors'");
    try requireContains(install_zig_source, "'--continue-at'");
    try requireContains(install_zig_source, "'--output'");
    try requireContains(install_zig_source, "subprocess.run(cmd, check=True)");
}

test "install-zig keeps the Python fallback resumable and fail-closed" {
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
    try requireContains(install_zig_source, "if not append and destination.exists():");
    try requireContains(install_zig_source, "destination.unlink()");
    try requireOrder(
        install_zig_source,
        "except (FileNotFoundError, subprocess.CalledProcessError) as exc:",
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
    );
    try requireContains(install_zig_source, "assert range_header == 'bytes=4-'");
    try requireContains(install_zig_source, "assert temp_path.read_bytes() == b'zig-data'");
}

test "installer action path remains tied to the pinned canonical release and workflow self-test" {
    const bootstrap_workflow = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(bootstrap_workflow);

    if (std.mem.indexOf(u8, install_zig_source, "CANONICAL_RELEASE_CHANNEL") != null) {
        try requireContains(install_zig_source, "CANONICAL_RELEASE_CHANNEL = '0.17.0-dev.758+748e7c5e3'");
        try requireContains(install_zig_source, "CANONICAL_RELEASE_REPO = os.environ.get('ZIGUX_ZIG_RELEASE_REPO', 'adybag14-cyber/zig')");
        try requireContains(install_zig_source, "CANONICAL_RELEASE_TAG = os.environ.get('ZIGUX_ZIG_RELEASE_TAG', 'upstream-748e7c5e39fc')");
    }
    try requireContains(install_zig_source, "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'");
    try requireContains(install_zig_source, "print('ZIG_INSTALL_STATUS=resolved')");
    try requireContains(install_zig_source, "print('ZIG_INSTALL_STATUS=pass')");

    try requireContains(bootstrap_workflow, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true");
    try std.testing.expect(
        std.mem.indexOf(u8, bootstrap_workflow, "Self-test current Zig installer helper") != null or
            std.mem.indexOf(u8, bootstrap_workflow, "Self-test Zig installer") != null,
    );
    try requireExactlyOnce(bootstrap_workflow, "python3 scripts/zigux/install-zig.py --self-test");
    if (std.mem.indexOf(u8, bootstrap_workflow, "Setup pinned Zig toolchain") != null) {
        try requireOrder(
            bootstrap_workflow,
            "Setup pinned Zig toolchain",
            "python3 scripts/zigux/install-zig.py --self-test",
        );
    }
}
