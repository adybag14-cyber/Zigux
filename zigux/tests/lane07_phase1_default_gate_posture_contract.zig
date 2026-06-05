const std = @import("std");
const contract_options = @import("contract_options");

const tests_build_source = @embedFile(contract_options.tests_build_path);

fn requireMarker(marker: []const u8) !void {
    if (std.mem.indexOf(u8, tests_build_source, marker) == null) {
        std.debug.print("missing tests-root build marker: {s}\n", .{marker});
        return error.MissingBuildMarker;
    }
}

fn markerIndex(marker: []const u8) !usize {
    return std.mem.indexOf(u8, tests_build_source, marker) orelse {
        std.debug.print("missing tests-root build marker: {s}\n", .{marker});
        return error.MissingBuildMarker;
    };
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = try markerIndex(before);
    const after_index = try markerIndex(after);
    if (before_index >= after_index) {
        std.debug.print(
            "tests-root build marker order drifted: {s} should precede {s}\n",
            .{ before, after },
        );
        return error.BuildMarkerOrderDrift;
    }
}

fn requireCount(marker: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, tests_build_source[offset..], marker)) |relative_index| {
        count += 1;
        offset += relative_index + marker.len;
    }
    if (count != expected) {
        std.debug.print(
            "tests-root build marker count drifted for {s}: expected {d}, found {d}\n",
            .{ marker, expected, count },
        );
        return error.BuildMarkerCountDrift;
    }
}

fn sliceBetween(start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = try markerIndex(start_marker);
    const end = try markerIndex(end_marker);
    if (start >= end) {
        std.debug.print(
            "tests-root build slice order drifted: {s} should precede {s}\n",
            .{ start_marker, end_marker },
        );
        return error.BuildMarkerOrderDrift;
    }
    return tests_build_source[start..end];
}

fn requireAbsentInSlice(slice: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, slice, marker) != null) {
        std.debug.print("unexpected tests-root default-gate marker: {s}\n", .{marker});
        return error.UnexpectedDefaultGateMarker;
    }
}

test "lane07 default gate posture keeps both phase1 routes addressable" {
    try requireMarker("const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);");
    try requireMarker("const phase1_string_direct_anchor = addPhase1StringDirectAnchor(b, target, optimize);");
    try requireMarker(
        "const phase1_step = b.step(\n" ++
            "        \"phase1-host-tools-smoke\",\n" ++
            "        \"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\",\n" ++
            "    );",
    );
    try requireMarker(
        "const phase1_string_direct_anchor_step = b.step(\n" ++
            "        \"phase1-string-direct-anchor\",\n" ++
            "        \"Run the shared Phase 1 string strlcat direct-anchor packet from zigux/tests\",\n" ++
            "    );",
    );
    try requireMarker("phase1_step.dependOn(&phase1_host_tools_smoke.step);");
    try requireMarker("phase1_string_direct_anchor_step.dependOn(&phase1_string_direct_anchor.step);");
    try requireOrdered(
        "const phase1_step = b.step(",
        "const phase1_string_direct_anchor_step = b.step(",
    );
}

test "lane07 default gate posture keeps shared smoke on default gates" {
    try requireCount("smoke_step.dependOn(&phase1_host_tools_smoke.step);", 1);
    try requireCount("test_step.dependOn(&phase1_host_tools_smoke.step);", 1);
    try requireOrdered(
        "const smoke_step = b.step(",
        "smoke_step.dependOn(&phase1_host_tools_smoke.step);",
    );
    try requireOrdered(
        "const test_step = b.step(",
        "test_step.dependOn(&phase1_host_tools_smoke.step);",
    );
}

test "lane07 default gate posture keeps string direct-anchor opt-in" {
    const smoke_slice = try sliceBetween(
        "const smoke_step = b.step(",
        "const test_step = b.step(",
    );
    const test_slice = tests_build_source[try markerIndex("const test_step = b.step(")..];

    try requireAbsentInSlice(smoke_slice, "phase1_string_direct_anchor");
    try requireAbsentInSlice(test_slice, "phase1_string_direct_anchor");
    try requireAbsentInSlice(smoke_slice, "phase1-string-direct-anchor");
    try requireAbsentInSlice(test_slice, "phase1-string-direct-anchor");
}
