const std = @import("std");

const current_build_gate_slice =
    \\    const phase1_step = b.step(
    \\        "phase1-host-tools-smoke",
    \\        "Run the shared Phase 1 host-tools smoke anchor from zigux/tests",
    \\    );
    \\    phase1_step.dependOn(&phase1_host_tools_smoke.step);
    \\
    \\    const phase1_string_direct_anchor_step = b.step(
    \\        "phase1-string-direct-anchor",
    \\        "Run the shared Phase 1 string strlcat direct-anchor packet from zigux/tests",
    \\    );
    \\    phase1_string_direct_anchor_step.dependOn(&phase1_string_direct_anchor.step);
    \\
    \\    const smoke_step = b.step(
    \\        "smoke",
    \\        "Run the currently live shared survey anchors from zigux/tests",
    \\    );
    \\    smoke_step.dependOn(&phase1_host_tools_smoke.step);
    \\    smoke_step.dependOn(phase3_test_step);
    \\
    \\    const test_step = b.step(
    \\        "test",
    \\        "Run the shared Zigux tests-root survey smoke",
    \\    );
    \\    test_step.dependOn(&phase1_host_tools_smoke.step);
    \\    test_step.dependOn(phase3_test_step);
;

const GatePosture = struct {
    host_smoke_step: []const u8,
    direct_anchor_step: []const u8,
    smoke_step: []const u8,
    test_step: []const u8,
};

fn sectionFrom(source: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, source, start_marker) orelse return error.MissingStartMarker;
    const body_start = start + start_marker.len;
    const end_relative = std.mem.indexOf(u8, source[body_start..], end_marker) orelse return error.MissingEndMarker;
    return source[start .. body_start + end_relative];
}

fn parseGatePosture(build_zig: []const u8) !GatePosture {
    return .{
        .host_smoke_step = try sectionFrom(
            build_zig,
            "const phase1_step = b.step(",
            "const phase1_string_direct_anchor_step = b.step(",
        ),
        .direct_anchor_step = try sectionFrom(
            build_zig,
            "const phase1_string_direct_anchor_step = b.step(",
            "const smoke_step = b.step(",
        ),
        .smoke_step = try sectionFrom(
            build_zig,
            "const smoke_step = b.step(",
            "const test_step = b.step(",
        ),
        .test_step = build_zig[std.mem.indexOf(u8, build_zig, "const test_step = b.step(") orelse return error.MissingTestStepMarker ..],
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "Phase 1 host-tools smoke remains the default Phase 1 route" {
    const gates = try parseGatePosture(current_build_gate_slice);

    try expectContains(gates.host_smoke_step, "\"phase1-host-tools-smoke\"");
    try expectContains(gates.host_smoke_step, "phase1_step.dependOn(&phase1_host_tools_smoke.step)");
    try expectNotContains(gates.host_smoke_step, "phase1_string_direct_anchor.step");
}

test "Phase 1 string direct anchor remains separately addressable" {
    const gates = try parseGatePosture(current_build_gate_slice);

    try expectContains(gates.direct_anchor_step, "\"phase1-string-direct-anchor\"");
    try expectContains(gates.direct_anchor_step, "phase1_string_direct_anchor_step.dependOn(&phase1_string_direct_anchor.step)");
    try expectNotContains(gates.direct_anchor_step, "phase1_host_tools_smoke.step");
}

test "smoke and test gates keep direct-anchor opt-in only" {
    const gates = try parseGatePosture(current_build_gate_slice);

    try expectContains(gates.smoke_step, "smoke_step.dependOn(&phase1_host_tools_smoke.step)");
    try expectContains(gates.test_step, "test_step.dependOn(&phase1_host_tools_smoke.step)");
    try expectNotContains(gates.smoke_step, "phase1_string_direct_anchor.step");
    try expectNotContains(gates.test_step, "phase1_string_direct_anchor.step");
}
