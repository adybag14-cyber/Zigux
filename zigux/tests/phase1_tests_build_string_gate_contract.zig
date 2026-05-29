const std = @import("std");

const build_zig = @embedFile("build.zig");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, build_zig, needle) != null);
}

fn expectBefore(earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, build_zig, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, build_zig, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "phase1 tests build keeps host-tools and string direct-anchor runners live" {
    try expectContains("fn addPhase1HostToolsSmoke(");
    try expectContains(".root_source_file = b.path(\"phase1_host_tools_smoke.zig\")");
    try expectContains("const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);");
    try expectContains("phase1_step.dependOn(&phase1_host_tools_smoke.step);");

    try expectContains("fn addPhase1StringDirectAnchor(");
    try expectContains(".root_source_file = b.path(\"../../tools/lib/string_phase1_strlcat_test.zig\")");
    try expectContains("const phase1_string_direct_anchor = addPhase1StringDirectAnchor(b, target, optimize);");
    try expectContains("phase1_string_direct_anchor_step.dependOn(&phase1_string_direct_anchor.step);");
}

test "phase1 tests build exposes the shared and focused Phase 1 gate steps in order" {
    try expectBefore(
        "const phase1_step = b.step(\n        \"phase1-host-tools-smoke\"",
        "const phase1_string_direct_anchor_step = b.step(\n        \"phase1-string-direct-anchor\"",
    );
    try expectBefore(
        "const phase1_string_direct_anchor_step = b.step(\n        \"phase1-string-direct-anchor\"",
        "const phase3_step = b.step(\n        \"phase3-dev-t-starter-packet\"",
    );
}

test "phase1 aggregate smoke and test gates still include the host-tools smoke runner" {
    try expectBefore(
        "const smoke_step = b.step(\n        \"smoke\"",
        "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    );
    try expectBefore(
        "const test_step = b.step(\n        \"test\"",
        "test_step.dependOn(&phase1_host_tools_smoke.step);",
    );
}
