const std = @import("std");
const build_options = @import("build_options");

const workflow_path = build_options.workflow_path;

const WorkflowError = error{
    DuplicateMarker,
    MissingMarker,
    MisorderedMarker,
};

const Marker = struct {
    name: []const u8,
    needle: []const u8,
};

const trigger_markers = [_]Marker{
    .{ .name = "master push trigger", .needle = "  push:\n    branches: [ master ]" },
    .{ .name = "pull request trigger", .needle = "  pull_request:\n    paths:" },
    .{ .name = "manual trigger", .needle = "  workflow_dispatch:" },
};

const required_path_filters = [_]Marker{
    .{ .name = "lib subtree", .needle = "      - 'lib/**'" },
    .{ .name = "alpha subtree", .needle = "      - 'zigux-alpha/**'" },
    .{ .name = "docs subtree", .needle = "      - 'Documentation/zigux/**'" },
    .{ .name = "samples subtree", .needle = "      - 'samples/zigux/**'" },
    .{ .name = "kernel zig files", .needle = "      - 'kernel/**/*.zig'" },
    .{ .name = "net zig files", .needle = "      - 'net/**/*.zig'" },
    .{ .name = "driver zig files", .needle = "      - 'drivers/**/*.zig'" },
    .{ .name = "fixdep C source", .needle = "      - 'scripts/basic/fixdep.c'" },
    .{ .name = "xalloc C helper", .needle = "      - 'scripts/include/xalloc.h'" },
    .{ .name = "kconfig conf source", .needle = "      - 'scripts/kconfig/conf.c'" },
    .{ .name = "kconfig confdata source", .needle = "      - 'scripts/kconfig/confdata.c'" },
    .{ .name = "scripts Zigux subtree", .needle = "      - 'scripts/zigux/**'" },
    .{ .name = "trusted archive subtree", .needle = "      - 'third_party/**'" },
    .{ .name = "top-level tools lib Zig files", .needle = "      - 'tools/lib/*.zig'" },
    .{ .name = "nested tools lib Zig files", .needle = "      - 'tools/lib/**/*.zig'" },
    .{ .name = "subcmd exec C helper", .needle = "      - 'tools/lib/subcmd/exec-cmd.c'" },
    .{ .name = "subcmd help C helper", .needle = "      - 'tools/lib/subcmd/help.c'" },
    .{ .name = "kallsyms C helper", .needle = "      - 'tools/lib/symbol/kallsyms.c'" },
    .{ .name = "Zigux support subtree", .needle = "      - 'zigux/**'" },
    .{ .name = "linux Zigux header", .needle = "      - 'include/linux/zigux.h'" },
    .{ .name = "Zigux include subtree", .needle = "      - 'include/zigux/**'" },
    .{ .name = "workflow self trigger", .needle = "      - '.github/workflows/zigux-bootstrap.yml'" },
};

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

fn requireUnique(haystack: []const u8, marker: Marker) !usize {
    const first = std.mem.indexOf(u8, haystack, marker.needle) orelse {
        _ = marker.name;
        return WorkflowError.MissingMarker;
    };
    if (std.mem.indexOf(u8, haystack[first + marker.needle.len ..], marker.needle) != null) {
        _ = marker.name;
        return WorkflowError.DuplicateMarker;
    }
    return first;
}

fn requireOrdered(haystack: []const u8, markers: []const Marker) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const index = try requireUnique(haystack, marker);
        if (index < cursor) {
            _ = marker.name;
            return WorkflowError.MisorderedMarker;
        }
        cursor = index + marker.needle.len;
    }
}

fn requireTriggerEnvelope(workflow: []const u8) !void {
    try requireOrdered(workflow, trigger_markers[0..]);
}

fn requirePullRequestPathFilters(workflow: []const u8) !void {
    const pull_request_index = try requireUnique(workflow, .{
        .name = "pull request paths header",
        .needle = "  pull_request:\n    paths:",
    });
    const manual_trigger_index = try requireUnique(workflow, .{
        .name = "workflow dispatch trigger",
        .needle = "  workflow_dispatch:",
    });
    if (manual_trigger_index < pull_request_index) {
        return WorkflowError.MisorderedMarker;
    }
    const pull_request_block = workflow[pull_request_index..manual_trigger_index];
    try requireOrdered(pull_request_block, required_path_filters[0..]);
}

test "workflow keeps master push pull-request filters and manual trigger envelope" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    try requireTriggerEnvelope(workflow);
}

test "workflow keeps all Zigux-relevant pull request path filters ordered and unique" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    try requirePullRequestPathFilters(workflow);
}

test "missing scripts Zigux path filter fails closed" {
    const workflow =
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\    paths:
        \\      - 'lib/**'
        \\      - 'zigux-alpha/**'
        \\      - 'Documentation/zigux/**'
        \\      - 'samples/zigux/**'
        \\      - 'kernel/**/*.zig'
        \\      - 'net/**/*.zig'
        \\      - 'drivers/**/*.zig'
        \\      - 'scripts/basic/fixdep.c'
        \\      - 'scripts/include/xalloc.h'
        \\      - 'scripts/kconfig/conf.c'
        \\      - 'scripts/kconfig/confdata.c'
        \\      - 'third_party/**'
        \\      - 'tools/lib/*.zig'
        \\      - 'tools/lib/**/*.zig'
        \\      - 'tools/lib/subcmd/exec-cmd.c'
        \\      - 'tools/lib/subcmd/help.c'
        \\      - 'tools/lib/symbol/kallsyms.c'
        \\      - 'zigux/**'
        \\      - 'include/linux/zigux.h'
        \\      - 'include/zigux/**'
        \\      - '.github/workflows/zigux-bootstrap.yml'
        \\  workflow_dispatch:
    ;

    try std.testing.expectError(WorkflowError.MissingMarker, requirePullRequestPathFilters(workflow));
}

test "duplicate tools lib glob fails closed" {
    const workflow =
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\    paths:
        \\      - 'lib/**'
        \\      - 'zigux-alpha/**'
        \\      - 'Documentation/zigux/**'
        \\      - 'samples/zigux/**'
        \\      - 'kernel/**/*.zig'
        \\      - 'net/**/*.zig'
        \\      - 'drivers/**/*.zig'
        \\      - 'scripts/basic/fixdep.c'
        \\      - 'scripts/include/xalloc.h'
        \\      - 'scripts/kconfig/conf.c'
        \\      - 'scripts/kconfig/confdata.c'
        \\      - 'scripts/zigux/**'
        \\      - 'third_party/**'
        \\      - 'tools/lib/*.zig'
        \\      - 'tools/lib/*.zig'
        \\      - 'tools/lib/**/*.zig'
        \\      - 'tools/lib/subcmd/exec-cmd.c'
        \\      - 'tools/lib/subcmd/help.c'
        \\      - 'tools/lib/symbol/kallsyms.c'
        \\      - 'zigux/**'
        \\      - 'include/linux/zigux.h'
        \\      - 'include/zigux/**'
        \\      - '.github/workflows/zigux-bootstrap.yml'
        \\  workflow_dispatch:
    ;

    try std.testing.expectError(WorkflowError.DuplicateMarker, requirePullRequestPathFilters(workflow));
}
