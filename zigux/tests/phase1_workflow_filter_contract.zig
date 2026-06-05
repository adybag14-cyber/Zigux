const std = @import("std");
const options = @import("phase1_workflow_filter_options");

const workflow = options.workflow;

const path_filters = [_][]const u8{
    "      - 'lib/**'\n",
    "      - 'zigux-alpha/**'\n",
    "      - 'Documentation/zigux/**'\n",
    "      - 'samples/zigux/**'\n",
    "      - 'kernel/**/*.zig'\n",
    "      - 'net/**/*.zig'\n",
    "      - 'drivers/**/*.zig'\n",
    "      - 'scripts/basic/fixdep.c'\n",
    "      - 'scripts/include/xalloc.h'\n",
    "      - 'scripts/kconfig/conf.c'\n",
    "      - 'scripts/kconfig/confdata.c'\n",
    "      - 'scripts/zigux/**'\n",
    "      - 'third_party/**'\n",
    "      - 'tools/lib/*.zig'\n",
    "      - 'tools/lib/**/*.zig'\n",
    "      - 'tools/lib/subcmd/exec-cmd.c'\n",
    "      - 'tools/lib/subcmd/help.c'\n",
    "      - 'tools/lib/symbol/kallsyms.c'\n",
    "      - 'zigux/**'\n",
    "      - 'include/linux/zigux.h'\n",
    "      - 'include/zigux/**'\n",
    "      - '.github/workflows/zigux-bootstrap.yml'\n",
};

const stale_filters = [_][]const u8{
    "      - 'scripts/zigux/*.py'\n",
    "      - 'tools/lib/bitmap.zig'\n",
    "      - 'tools/lib/find_bit.zig'\n",
    "      - 'tools/lib/string.zig'\n",
    "      - 'tools/lib/rbtree.zig'\n",
    "      - 'zigux/tests/**'\n",
};

fn sliceBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingStartMarker;
    const after_start = start + start_marker.len;
    const relative_end = std.mem.indexOf(u8, haystack[after_start..], end_marker) orelse return error.MissingEndMarker;
    return haystack[after_start .. after_start + relative_end];
}

fn indexAfter(haystack: []const u8, needle: []const u8, offset: usize) ?usize {
    const relative = std.mem.indexOf(u8, haystack[offset..], needle) orelse return null;
    return offset + relative;
}

fn expectUnique(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingWorkflowMarker;
    const after_first = first + needle.len;
    try std.testing.expect(std.mem.indexOf(u8, haystack[after_first..], needle) == null);
    return first;
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "master pushes keep exact-head bootstrap unfiltered" {
    try std.testing.expect(std.mem.indexOf(
        u8,
        workflow,
        "# Run every master push so exact-head bootstrap status stays attached even when path filtering misses a live change.\n",
    ) != null);

    const push_block = try sliceBetween(workflow, "  push:\n", "  pull_request:\n");
    try std.testing.expect(std.mem.indexOf(u8, push_block, "    branches: [ master ]\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, push_block, "    paths:\n") == null);
}

test "pull request filters keep phase1 helper harness surfaces visible" {
    const pull_request_block = try sliceBetween(workflow, "  pull_request:\n", "  workflow_dispatch:\n");
    _ = try expectUnique(pull_request_block, "    paths:\n");

    var cursor: usize = 0;
    for (path_filters) |path_filter| {
        const next = indexAfter(pull_request_block, path_filter, cursor) orelse return error.MissingPathFilter;
        cursor = next + path_filter.len;
    }
}

test "phase1 helper path filters stay scoped to current checkout surfaces" {
    const pull_request_block = try sliceBetween(workflow, "  pull_request:\n", "  workflow_dispatch:\n");
    _ = try expectUnique(pull_request_block, "      - 'scripts/zigux/**'\n");
    _ = try expectUnique(pull_request_block, "      - 'tools/lib/*.zig'\n");
    _ = try expectUnique(pull_request_block, "      - 'tools/lib/**/*.zig'\n");
    _ = try expectUnique(pull_request_block, "      - 'zigux/**'\n");
    _ = try expectUnique(pull_request_block, "      - '.github/workflows/zigux-bootstrap.yml'\n");
}

test "phase1 workflow filter rejects stale narrow helper harness filters" {
    const push_block = try sliceBetween(workflow, "  push:\n", "  pull_request:\n");
    const pull_request_block = try sliceBetween(workflow, "  pull_request:\n", "  workflow_dispatch:\n");

    try expectMissing(push_block, "    paths:\n");
    for (stale_filters) |stale_filter| {
        try expectMissing(pull_request_block, stale_filter);
    }
    try expectMissing(pull_request_block, "      - 'tools/lib/*.c'\n");
    try expectMissing(pull_request_block, "      - 'scripts/zigux/check-phase1-*.py'\n");
}
