const std = @import("std");
const build_options = @import("build_options");

const workflow = @embedFile(build_options.workflow_path);
const make_prefix = "        run: make -C zigux ";

const expected_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-fixdep",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-validate",
    "phase2",
    "phase3-policy-starter-packet-test",
    "phase3-policy-unsafe-test",
    "phase3-policy-dump",
    "phase3-low-level-wrappers",
    "phase3-low-level-wrappers-test",
    "phase4-validate",
    "phase4-test",
    "phase4-artifact-diff-contract",
    "phase6-validate",
    "phase6-perf",
    "phase8-validate",
    "phase8-exec-cmd-test",
    "phase8-libbpf-segments-test",
    "phase8-test",
    "phase10-validate",
    "phase10-test",
    "phase11-validate",
    "phase12-smoke",
    "phase12-test",
    "phase12",
    "phase12-virtio-net-syntax-lab-test",
    "phase14-validate",
};

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingWorkflowMarker;
}

fn requireOrdered(markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = requireContains(workflow[cursor..], marker) catch |err| {
            std.debug.print("missing workflow marker: {s}\n", .{marker});
            return err;
        };
        cursor += found + marker.len;
    }
}

fn nextLineAfter(offset: usize) []const u8 {
    const line_start = offset + make_prefix.len;
    const line_end = std.mem.indexOfScalar(u8, workflow[line_start..], '\n') orelse workflow[line_start..].len;
    return workflow[line_start .. line_start + line_end];
}

test "workflow keeps exact make route roster" {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, workflow[cursor..], make_prefix)) |relative| {
        if (count >= expected_routes.len) {
            return error.UnexpectedMakeRoute;
        }

        const offset = cursor + relative;
        const route_line = nextLineAfter(offset);
        const expected = expected_routes[count];
        if (!std.mem.eql(u8, route_line, expected)) {
            std.debug.print(
                "unexpected make route at index {d}: got {s}, expected {s}\n",
                .{ count, route_line, expected },
            );
            return error.MakeRouteRosterMismatch;
        }

        cursor = offset + make_prefix.len + route_line.len;
        count += 1;
    }

    try std.testing.expectEqual(expected_routes.len, count);
}

test "phase make routes remain in bootstrap execution order" {
    var ordered_markers: [expected_routes.len][]const u8 = undefined;
    var marker_storage: [expected_routes.len][128]u8 = undefined;

    for (&expected_routes, 0..) |route, index| {
        ordered_markers[index] = try std.fmt.bufPrint(&marker_storage[index], "{s}{s}\n", .{ make_prefix, route });
    }

    try requireOrdered(&ordered_markers);
}

test "route names remain scoped to explicit phase packets" {
    for (&expected_routes) |route| {
        try std.testing.expect(std.mem.startsWith(u8, route, "phase"));
        try std.testing.expect(std.mem.indexOfScalar(u8, route, ' ') == null);
        try std.testing.expect(std.mem.indexOfScalar(u8, route, ';') == null);
        try std.testing.expect(std.mem.indexOf(u8, route, "&&") == null);
    }
}
