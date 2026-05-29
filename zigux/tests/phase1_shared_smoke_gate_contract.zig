const std = @import("std");

const build_zig = @embedFile("build.zig");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
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

test "shared tests root exposes phase1 host-tools smoke as a named gate" {
    try requireContains(build_zig, "fn addPhase1HostToolsSmoke(");
    try requireContains(build_zig, ".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")");
    try requireContains(build_zig, ".name = \"phase1-host-tools-smoke\"");

    const step = try stepBlock("phase1_step");
    try requireContains(step, "\"phase1-host-tools-smoke\"");
    try requireContains(step, "phase1_step.dependOn(&phase1_host_tools_smoke.step);");
}

test "smoke gate keeps the Phase 1 harness ahead of later shared slices" {
    const smoke = try stepBlock("smoke_step");
    try requireContains(smoke, "\"smoke\"");
    try requireContains(smoke, "smoke_step.dependOn(&phase1_host_tools_smoke.step);");
    try requireContains(smoke, "smoke_step.dependOn(phase3_test_step);");

    const phase1_index = std.mem.indexOf(
        u8,
        smoke,
        "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    ).?;
    const phase3_index = std.mem.indexOf(u8, smoke, "smoke_step.dependOn(phase3_test_step);").?;
    try std.testing.expect(phase1_index < phase3_index);
}

test "default test gate mirrors the shared smoke Phase 1 dependency" {
    const test_gate = try stepBlock("test_step");
    try requireContains(test_gate, "\"test\"");
    try requireContains(test_gate, "test_step.dependOn(&phase1_host_tools_smoke.step);");
    try requireContains(test_gate, "test_step.dependOn(phase3_test_step);");

    try std.testing.expectEqual(
        @as(usize, 3),
        countOccurrences(build_zig, ".dependOn(&phase1_host_tools_smoke.step);"),
    );
}
