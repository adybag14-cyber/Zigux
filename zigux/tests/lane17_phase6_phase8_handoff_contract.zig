const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn loadWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(1024 * 1024));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(haystack, needle));
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, needle) orelse return error.MissingWorkflowMarker;
        cursor = found + needle.len;
    }
}

fn phase6Phase8MarkersStayOrdered(workflow: []const u8) !void {
    const ordered_markers = [_][]const u8{
        "- name: Validate current Phase 6 helper packet",
        "run: make -C zigux phase6-validate",
        "- name: Run current Phase 6 leaf helper tests",
        "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "- name: Run current Phase 6 shared perf route",
        "run: make -C zigux phase6-perf",
        "- name: Validate Phase 8 tooling routes",
        "run: make -C zigux phase8-validate",
        "- name: Run focused Phase 8 exec-cmd tests",
        "run: make -C zigux phase8-exec-cmd-test",
        "- name: Run focused Phase 8 libbpf segment tests",
        "run: make -C zigux phase8-libbpf-segments-test",
        "- name: Run Phase 8 tooling tests",
        "run: make -C zigux phase8-test",
    };

    try requireOrdered(workflow, &ordered_markers);
}

test "Lane 17 Phase 6 handoff reaches Phase 8 tooling only after Phase 6 perf" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try phase6Phase8MarkersStayOrdered(workflow);
}

test "Lane 17 Phase 6 to Phase 8 handoff keeps exact commands unique" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const required_once = [_][]const u8{
        "run: make -C zigux phase6-validate",
        "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "run: make -C zigux phase6-perf",
        "run: make -C zigux phase8-validate",
        "run: make -C zigux phase8-exec-cmd-test",
        "run: make -C zigux phase8-libbpf-segments-test",
        "run: make -C zigux phase8-test",
    };
    for (required_once) |needle| {
        try requireOnce(workflow, needle);
    }

    try requireAbsent(workflow, "run: make -C zigux phase8\n");
    try requireAbsent(workflow, "run: zig build test --build-file zigux/tests/phase8_build.zig");
    try requireAbsent(workflow, "run: make -C zigux phase6-test");
}

test "Lane 17 Phase 6 to Phase 8 handoff rejects missing duplicate and reordered gates" {
    const good =
        \\- name: Validate current Phase 6 helper packet
        \\  run: make -C zigux phase6-validate
        \\- name: Run current Phase 6 leaf helper tests
        \\  run: zig build test --build-file zigux/tests/phase6_build.zig --summary all
        \\- name: Run current Phase 6 shared perf route
        \\  run: make -C zigux phase6-perf
        \\- name: Validate Phase 8 tooling routes
        \\  run: make -C zigux phase8-validate
        \\- name: Run focused Phase 8 exec-cmd tests
        \\  run: make -C zigux phase8-exec-cmd-test
        \\- name: Run focused Phase 8 libbpf segment tests
        \\  run: make -C zigux phase8-libbpf-segments-test
        \\- name: Run Phase 8 tooling tests
        \\  run: make -C zigux phase8-test
        \\
    ;
    try phase6Phase8MarkersStayOrdered(good);

    const missing_phase8_validate = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        good,
        "- name: Validate Phase 8 tooling routes\n  run: make -C zigux phase8-validate\n",
        "",
    ) catch unreachable;
    defer std.testing.allocator.free(missing_phase8_validate);
    try std.testing.expectError(error.MissingWorkflowMarker, phase6Phase8MarkersStayOrdered(missing_phase8_validate));

    const duplicate_phase8_validate = try std.mem.concat(std.testing.allocator, u8, &.{
        good,
        "- name: Validate Phase 8 tooling routes\n  run: make -C zigux phase8-validate\n",
    });
    defer std.testing.allocator.free(duplicate_phase8_validate);
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(duplicate_phase8_validate, "run: make -C zigux phase8-validate"));

    const reordered =
        \\- name: Validate Phase 8 tooling routes
        \\  run: make -C zigux phase8-validate
        \\- name: Validate current Phase 6 helper packet
        \\  run: make -C zigux phase6-validate
        \\- name: Run current Phase 6 leaf helper tests
        \\  run: zig build test --build-file zigux/tests/phase6_build.zig --summary all
        \\- name: Run current Phase 6 shared perf route
        \\  run: make -C zigux phase6-perf
        \\- name: Run focused Phase 8 exec-cmd tests
        \\  run: make -C zigux phase8-exec-cmd-test
        \\- name: Run focused Phase 8 libbpf segment tests
        \\  run: make -C zigux phase8-libbpf-segments-test
        \\- name: Run Phase 8 tooling tests
        \\  run: make -C zigux phase8-test
        \\
    ;
    try std.testing.expectError(error.MissingWorkflowMarker, phase6Phase8MarkersStayOrdered(reordered));
}
