const std = @import("std");

const Route = struct {
    name: []const u8,
    command: []const u8,
    owner: []const u8,
};

const closure_validator = Route{
    .name = "PHASE1_CLOSURE_VALIDATOR",
    .command = "python3 scripts/zigux/validate-phase1-closure.py",
    .owner = "closure-note",
};

const route_summary_guard = Route{
    .name = "PHASE1_ROUTE_SUMMARY_GUARD",
    .command = "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    .owner = "workflow-and-makefile",
};

const shared_tests_route = Route{
    .name = "PHASE1_SHARED_TESTS_ROUTE",
    .command = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    .owner = "tests-root",
};

const closure_routes = [_]Route{
    closure_validator,
    route_summary_guard,
    shared_tests_route,
};

const required_route_names = [_][]const u8{
    "PHASE1_CLOSURE_VALIDATOR",
    "PHASE1_ROUTE_SUMMARY_GUARD",
    "PHASE1_SHARED_TESTS_ROUTE",
};

const expected_validators = [_][]const u8{
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "zigux/tests/build.zig",
};

fn hasNeedle(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn routeByName(name: []const u8) ?Route {
    for (closure_routes) |route| {
        if (std.mem.eql(u8, route.name, name)) return route;
    }
    return null;
}

test "phase1 closure validation routes stay explicitly named" {
    try std.testing.expectEqual(@as(usize, 3), closure_routes.len);

    for (required_route_names) |name| {
        const route = routeByName(name) orelse return error.MissingPhase1ClosureRoute;
        try std.testing.expect(hasNeedle(route.command, "phase1"));
        try std.testing.expect(route.owner.len > 0);
    }
}

test "phase1 closure validator remains the narrow authority route" {
    const route = routeByName("PHASE1_CLOSURE_VALIDATOR") orelse return error.MissingClosureValidator;

    try std.testing.expectEqualStrings("closure-note", route.owner);
    try std.testing.expectEqualStrings("python3 scripts/zigux/validate-phase1-closure.py", route.command);
    try std.testing.expect(!hasNeedle(route.command, "check-phase1-bench.py"));
    try std.testing.expect(!hasNeedle(route.command, "check-phase1-shared-reminder-packet.py"));
}

test "phase1 route summary guard stays separate from closure validator" {
    const route = routeByName("PHASE1_ROUTE_SUMMARY_GUARD") orelse return error.MissingRouteSummaryGuard;

    try std.testing.expectEqualStrings("workflow-and-makefile", route.owner);
    try std.testing.expect(hasNeedle(route.command, "check-phase1-route-summary-counts.py"));
    try std.testing.expect(!std.mem.eql(u8, route.command, closure_validator.command));
}

test "phase1 shared smoke route stays tests-root owned" {
    const route = routeByName("PHASE1_SHARED_TESTS_ROUTE") orelse return error.MissingSharedTestsRoute;

    try std.testing.expectEqualStrings("tests-root", route.owner);
    try std.testing.expect(hasNeedle(route.command, "phase1-host-tools-smoke"));
    try std.testing.expect(hasNeedle(route.command, "zigux/tests/build.zig"));
}

test "phase1 closure validation roster has no duplicate route commands" {
    for (closure_routes, 0..) |left, left_index| {
        for (closure_routes[left_index + 1 ..]) |right| {
            try std.testing.expect(!std.mem.eql(u8, left.command, right.command));
        }
    }
}

test "phase1 closure validation routes cover each expected validator path" {
    for (expected_validators) |validator| {
        var matched = false;
        for (closure_routes) |route| {
            matched = matched or hasNeedle(route.command, validator);
        }
        try std.testing.expect(matched);
    }
}
