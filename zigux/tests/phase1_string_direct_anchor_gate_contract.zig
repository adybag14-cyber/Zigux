const std = @import("std");

const build_zig = @embedFile("build.zig");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireMissing(haystack: []const u8, needle: []const u8) !void {
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

fn sliceAfter(needle: []const u8) ![]const u8 {
    const index = std.mem.indexOf(u8, build_zig, needle) orelse return error.MissingNeedle;
    return build_zig[index..];
}

fn blockAfter(marker: []const u8) ![]const u8 {
    const tail = try sliceAfter(marker);
    const next_marker = "\nfn ";
    if (std.mem.indexOf(u8, tail[marker.len..], next_marker)) |next_index| {
        return tail[0 .. marker.len + next_index];
    }
    return tail;
}

fn stepBlock(step_name: []const u8) ![]const u8 {
    const marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "const {s} = b.step(",
        .{step_name},
    );
    defer std.testing.allocator.free(marker);

    const tail = try sliceAfter(marker);
    const next_marker = "\n    const ";
    if (std.mem.indexOf(u8, tail[marker.len..], next_marker)) |next_index| {
        return tail[0 .. marker.len + next_index];
    }
    return tail;
}

test "string direct anchor keeps its helper-local root source" {
    const helper_block = try blockAfter("fn addPhase1StringDirectAnchor(");
    try requireContains(helper_block, ".root_source_file = b.path(\"../../tools/lib/string_phase1_strlcat_test.zig\")");
    try requireContains(helper_block, ".name = \"phase1-string-direct-anchor\"");
    try requireContains(build_zig, "const phase1_string_direct_anchor = addPhase1StringDirectAnchor(b, target, optimize);");
}

test "string direct anchor remains exposed as its own named gate" {
    const step = try stepBlock("phase1_string_direct_anchor_step");
    try requireContains(step, "\"phase1-string-direct-anchor\"");
    try requireContains(
        step,
        "phase1_string_direct_anchor_step.dependOn(&phase1_string_direct_anchor.step);",
    );

    try std.testing.expectEqual(
        @as(usize, 2),
        countOccurrences(build_zig, "\"phase1-string-direct-anchor\""),
    );
}

test "default smoke and test gates stay on the shared Phase 1 harness" {
    const smoke = try stepBlock("smoke_step");
    const test_gate = try stepBlock("test_step");

    try requireContains(smoke, "smoke_step.dependOn(&phase1_host_tools_smoke.step);");
    try requireContains(test_gate, "test_step.dependOn(&phase1_host_tools_smoke.step);");
    try requireMissing(smoke, "smoke_step.dependOn(&phase1_string_direct_anchor.step);");
    try requireMissing(test_gate, "test_step.dependOn(&phase1_string_direct_anchor.step);");
}
