const std = @import("std");

const WorkflowFile = struct {
    contents: []u8,
};

fn readWorkflow(path: []const u8) !WorkflowFile {
    return .{
        .contents = try std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            std.testing.allocator,
            .limited(512 * 1024),
        ),
    };
}

fn unloadWorkflow(file: WorkflowFile) void {
    std.testing.allocator.free(file.contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    return count;
}

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

test "lane17 setup python bridge remains pinned before pinned Zig setup" {
    const workflow = try readWorkflow(workflow_path);
    defer unloadWorkflow(workflow);

    try expectContains(workflow.contents, "- name: Checkout workspace snapshot");
    try expectContains(workflow.contents, "- name: Setup Python");
    try expectContains(workflow.contents, "uses: actions/setup-python@v6.2.0");
    try expectContains(workflow.contents, "python-version: '3.x'");
    try expectContains(workflow.contents, "- name: Setup pinned Zig toolchain");

    try expectBefore(workflow.contents, "- name: Checkout workspace snapshot", "- name: Setup Python");
    try expectBefore(workflow.contents, "- name: Setup Python", "- name: Setup pinned Zig toolchain");
    try expectBefore(workflow.contents, "uses: actions/setup-python@v6.2.0", "- name: Setup pinned Zig toolchain");
    try expectBefore(workflow.contents, "python-version: '3.x'", "- name: Setup pinned Zig toolchain");

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow.contents, "- name: Setup Python"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow.contents, "uses: actions/setup-python@v6.2.0"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow.contents, "uses: actions/setup-python@"));
}

test "lane17 setup python bridge guards pinned Zig policy and archive python handoff" {
    const workflow = try readWorkflow(workflow_path);
    defer unloadWorkflow(workflow);

    const pinned_zig_markers = [_][]const u8{
        "eval \"$(python3 - <<'PY'",
        "json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
        "python3 scripts/zigux/stage-pinned-zig-archive.py",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
        "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"",
    };
    inline for (pinned_zig_markers) |marker| {
        try expectContains(workflow.contents, marker);
        try expectBefore(workflow.contents, "- name: Setup Python", marker);
        try expectBefore(workflow.contents, marker, "- name: Compile current scripts");
    }

    try expectBefore(workflow.contents, "- name: Setup pinned Zig toolchain", "- name: Compile current scripts");
    try expectContains(workflow.contents, "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org");
}

test "lane17 setup python bridge keeps phase1 checks after python-backed setup corridor" {
    const workflow = try readWorkflow(workflow_path);
    defer unloadWorkflow(workflow);

    const phase1_markers = [_][]const u8{
        "- name: Self-test current Phase 1 direct-owner checker",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "- name: Check current Phase 1 direct-owner markers",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "- name: Self-test current Phase 1 closure validator",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "- name: Check current Phase 1 closure packet",
        "python3 scripts/zigux/validate-phase1-closure.py",
    };
    inline for (phase1_markers) |marker| {
        try expectContains(workflow.contents, marker);
        try expectBefore(workflow.contents, "- name: Setup Python", marker);
        try expectBefore(workflow.contents, "- name: Setup pinned Zig toolchain", marker);
    }

    try expectBefore(workflow.contents, "- name: Compile current scripts", "- name: Self-test current Phase 1 direct-owner checker");
    try expectBefore(workflow.contents, "- name: Check current Phase 1 closure packet", "- name: Self-test current Phase 3 interop packet");
}
