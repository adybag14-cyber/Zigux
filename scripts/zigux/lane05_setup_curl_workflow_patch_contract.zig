const std = @import("std");

const live_workflow_path = ".github/workflows/zigux-bootstrap.yml";

const required_retry_flags = [_][]const u8{
    "--fail",
    "--location",
    "--retry 5",
    "--retry-all-errors",
    "--retry-delay 3",
    "--connect-timeout 20",
    "--speed-limit 1024",
    "--speed-time 30",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expect(countOccurrences(haystack, needle) == expected);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectRetryFlagsOnBothSetupCurlFetches(workflow: []const u8) !void {
    for (required_retry_flags) |flag| {
        try expectExactCount(workflow, flag, 2);
    }
}

fn readLiveWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        live_workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn replaceFirstAlloc(allocator: std.mem.Allocator, haystack: []const u8, needle: []const u8, replacement: []const u8) ![]u8 {
    const index = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingReplacementMarker;
    const out_len = haystack.len - needle.len + replacement.len;
    const out = try allocator.alloc(u8, out_len);
    @memcpy(out[0..index], haystack[0..index]);
    @memcpy(out[index .. index + replacement.len], replacement);
    @memcpy(out[index + replacement.len ..], haystack[index + needle.len ..]);
    return out;
}

fn expectSetupCurlWorkflowPatch(workflow: []const u8) !void {
    try expectContains(workflow, "- name: Setup pinned Zig toolchain");
    try expectContains(workflow, "try_download() {");
    try expectContains(workflow, "local url=\"$1\"");
    try expectContains(workflow, "\"$url\"");
    try expectContains(workflow, "-o \"$archive_path\"");
    try expectContains(workflow, "https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow, "-o \"$mirror_file\"");
    try expectRetryFlagsOnBothSetupCurlFetches(workflow);

    try expectNotContains(workflow, "curl -L --fail \"$url\" -o \"$archive_path\"");
    try expectNotContains(workflow, "curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectContains(workflow, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try expectBefore(workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"", "https://ziglang.org/download/community-mirrors.txt");
    try expectBefore(workflow, "https://ziglang.org/download/community-mirrors.txt", "try_download \"$ZIGUX_ZIG_URL\"");
    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\"", "tar -xJf \"$archive_path\" -C .zig-toolchain");
}

test "live setup workflow carries retry flags on archive and mirror fetches" {
    const workflow = try readLiveWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try expectSetupCurlWorkflowPatch(workflow);
}

test "missing retry-all-errors on either setup curl fetch is rejected" {
    const workflow = try readLiveWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const weakened = try replaceFirstAlloc(std.testing.allocator, workflow, "--retry-all-errors", "");
    defer std.testing.allocator.free(weakened);

    try std.testing.expectError(error.TestUnexpectedResult, expectSetupCurlWorkflowPatch(weakened));
}

test "extra retry delay occurrence is rejected" {
    const workflow = try readLiveWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const duplicated = try replaceFirstAlloc(std.testing.allocator, workflow, "--retry-delay 3", "--retry-delay 3\n              --retry-delay 3");
    defer std.testing.allocator.free(duplicated);

    try std.testing.expectError(error.TestUnexpectedResult, expectSetupCurlWorkflowPatch(duplicated));
}

test "archive output marker remains required" {
    const workflow = try readLiveWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const without_archive_output = try replaceFirstAlloc(std.testing.allocator, workflow, "-o \"$archive_path\"", "");
    defer std.testing.allocator.free(without_archive_output);

    try std.testing.expectError(error.TestUnexpectedResult, expectSetupCurlWorkflowPatch(without_archive_output));
}

test "verification marker remains before extraction" {
    const workflow = try readLiveWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const without_verification = try replaceFirstAlloc(
        std.testing.allocator,
        workflow,
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\"",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$missing_archive_path\"",
    );
    defer std.testing.allocator.free(without_verification);

    try std.testing.expectError(error.MissingFirstMarker, expectSetupCurlWorkflowPatch(without_verification));
}
