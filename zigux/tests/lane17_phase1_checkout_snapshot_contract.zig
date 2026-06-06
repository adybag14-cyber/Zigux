const std = @import("std");
const build_options = @import("build_options");

const WorkflowError = error{
    MissingMarker,
    ReorderedMarker,
    DuplicateMarker,
    StaleCheckoutAction,
    UnsafeSnapshotSource,
};

const checkout_markers = [_][]const u8{
    "- name: Checkout workspace snapshot",
    "run: |",
    "set -euxo pipefail",
    "tmpdir=\"$(mktemp -d)\"",
    "archive=\"$tmpdir/source.tar.gz\"",
    "curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"",
    "tar -xzf \"$archive\" -C \"$tmpdir\"",
    "src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"",
    "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +",
    "shopt -s dotglob",
    "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/",
};

fn readFileAlloc(path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(256 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return WorkflowError.MissingMarker;
    if (countOccurrences(haystack, needle) != 1) return WorkflowError.DuplicateMarker;
    return first;
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, marker) orelse {
            if (std.mem.indexOf(u8, haystack, marker) != null) return WorkflowError.ReorderedMarker;
            return WorkflowError.MissingMarker;
        };
        cursor = found + marker.len;
    }
}

fn validateCheckoutSnapshot(workflow: []const u8) !void {
    if (std.mem.indexOf(u8, workflow, "uses: actions/checkout") != null) {
        return WorkflowError.StaleCheckoutAction;
    }
    if (std.mem.indexOf(u8, workflow, "tar.gz/${GITHUB_REF}") != null or
        std.mem.indexOf(u8, workflow, "tar.gz/master") != null)
    {
        return WorkflowError.UnsafeSnapshotSource;
    }

    const checkout_index = try requireOnce(workflow, "- name: Checkout workspace snapshot");
    const setup_python_index = try requireOnce(workflow, "- name: Setup Python");
    const setup_zig_index = try requireOnce(workflow, "- name: Setup pinned Zig toolchain");
    if (setup_python_index <= checkout_index or setup_zig_index <= setup_python_index) {
        return WorkflowError.ReorderedMarker;
    }

    try requireOrdered(workflow, checkout_markers[0..]);
}

test "live bootstrap workflow keeps exact-head tarball checkout before setup" {
    const workflow = try readFileAlloc(build_options.workflow_path);
    defer std.testing.allocator.free(workflow);
    try validateCheckoutSnapshot(workflow);
}

test "contract rejects stale checkout action or branch snapshots" {
    const stale_action =
        \\- name: Checkout workspace snapshot
        \\  uses: actions/checkout@v5
        \\- name: Setup Python
        \\- name: Setup pinned Zig toolchain
    ;
    try std.testing.expectError(WorkflowError.StaleCheckoutAction, validateCheckoutSnapshot(stale_action));

    const branch_snapshot =
        \\- name: Checkout workspace snapshot
        \\  run: |
        \\    set -euxo pipefail
        \\    tmpdir="$(mktemp -d)"
        \\    archive="$tmpdir/source.tar.gz"
        \\    curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/master" -o "$archive"
        \\    tar -xzf "$archive" -C "$tmpdir"
        \\    src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
        \\    find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
        \\    shopt -s dotglob
        \\    mv "$src_dir"/* "$GITHUB_WORKSPACE"/
        \\- name: Setup Python
        \\- name: Setup pinned Zig toolchain
    ;
    try std.testing.expectError(WorkflowError.UnsafeSnapshotSource, validateCheckoutSnapshot(branch_snapshot));
}

test "contract rejects incomplete or reordered workspace replacement" {
    const missing_dotglob =
        \\- name: Checkout workspace snapshot
        \\  run: |
        \\    set -euxo pipefail
        \\    tmpdir="$(mktemp -d)"
        \\    archive="$tmpdir/source.tar.gz"
        \\    curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" -o "$archive"
        \\    tar -xzf "$archive" -C "$tmpdir"
        \\    src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
        \\    find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
        \\    mv "$src_dir"/* "$GITHUB_WORKSPACE"/
        \\- name: Setup Python
        \\- name: Setup pinned Zig toolchain
    ;
    try std.testing.expectError(WorkflowError.MissingMarker, validateCheckoutSnapshot(missing_dotglob));

    const moved_before_wipe =
        \\- name: Checkout workspace snapshot
        \\  run: |
        \\    set -euxo pipefail
        \\    tmpdir="$(mktemp -d)"
        \\    archive="$tmpdir/source.tar.gz"
        \\    curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" -o "$archive"
        \\    tar -xzf "$archive" -C "$tmpdir"
        \\    src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
        \\    shopt -s dotglob
        \\    mv "$src_dir"/* "$GITHUB_WORKSPACE"/
        \\    find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
        \\- name: Setup Python
        \\- name: Setup pinned Zig toolchain
    ;
    try std.testing.expectError(WorkflowError.ReorderedMarker, validateCheckoutSnapshot(moved_before_wipe));
}
