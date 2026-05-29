const std = @import("std");

const tests_build_zig = @embedFile("build.zig");

const shared_smoke_dependencies = [_][]const u8{
    "&phase1_host_tools_smoke.step",
    "phase3_test_step",
    "&phase4_runtime_atomic64_diff_survey.step",
    "&phase7_argv_split_survey.step",
    "phase8_host_tools_alpha_step",
    "&phase10_virtio_core_survey.step",
    "&phase10_virtio_ring_survey.step",
    "&phase10_virtio_input_survey.step",
    "&phase11_gpio_wdt_verify.step",
    "&phase12_virtio_net_survey.step",
    "&phase12_virtio_net_throughput_parity.step",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn sliceBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingStartMarker;
    const after_start = haystack[start..];
    const end = std.mem.indexOf(u8, after_start, end_marker) orelse return error.MissingEndMarker;
    return after_start[0..end];
}

fn sliceFrom(haystack: []const u8, start_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingStartMarker;
    return haystack[start..];
}

fn expectStepRoster(block: []const u8, step_var: []const u8) !void {
    try std.testing.expectEqual(@as(usize, shared_smoke_dependencies.len), std.mem.count(u8, block, ".dependOn("));

    for (shared_smoke_dependencies) |dependency| {
        var expected: [160]u8 = undefined;
        const line = try std.fmt.bufPrint(&expected, "{s}.dependOn({s});", .{ step_var, dependency });
        try expectContains(block, line);
    }
}

test "tests build keeps the Phase 1 helper harness routes named" {
    try expectContains(tests_build_zig, "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);");
    try expectContains(tests_build_zig, "const phase1_string_direct_anchor = addPhase1StringDirectAnchor(b, target, optimize);");
    try expectContains(tests_build_zig, "\"phase1-host-tools-smoke\",");
    try expectContains(tests_build_zig, "\"phase1-string-direct-anchor\",");
}

test "shared smoke step carries the current tests root workflow roster" {
    const smoke_block = try sliceBetween(
        tests_build_zig,
        "const smoke_step = b.step(",
        "const test_step = b.step(",
    );

    try expectStepRoster(smoke_block, "smoke_step");
    try expectAbsent(smoke_block, "phase1_string_direct_anchor.step");
}

test "default test step mirrors the shared smoke roster" {
    const test_block = try sliceFrom(tests_build_zig, "const test_step = b.step(");

    try expectStepRoster(test_block, "test_step");
    try expectAbsent(test_block, "phase1_string_direct_anchor.step");
}
