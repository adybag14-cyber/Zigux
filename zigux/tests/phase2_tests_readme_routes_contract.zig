const std = @import("std");

const phase2_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

test "tests README keeps Phase 2 route packet aligned with closure note" {
    const allocator = std.testing.allocator;
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure_note);

    try expectContains(tests_readme, "## Phase 2 review packet");
    try expectContains(tests_readme, "Keep the rematerialized make-wrapper packet explicit through");
    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=");

    var previous_tests_index: ?usize = null;
    var previous_closure_index: ?usize = null;

    for (phase2_routes) |route| {
        try expectContains(tests_readme, route);
        try expectContains(closure_note, route);

        const tests_route = try std.fmt.allocPrint(std.testing.allocator, "`{s}`", .{route});
        defer std.testing.allocator.free(tests_route);
        const tests_index = std.mem.indexOf(u8, tests_readme, tests_route).?;
        if (previous_tests_index) |previous| {
            try std.testing.expect(tests_index > previous);
        }
        previous_tests_index = tests_index;

        const closure_route = try closureRouteNeedle(std.testing.allocator, route);
        defer std.testing.allocator.free(closure_route);
        const closure_index = std.mem.indexOf(u8, closure_note, closure_route).?;
        if (previous_closure_index) |previous| {
            try std.testing.expect(closure_index > previous);
        }
        previous_closure_index = closure_index;
    }
}

test "tests README Phase 2 routes are declared in Makefile" {
    const allocator = std.testing.allocator;
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    for (phase2_routes) |route| {
        const target = route["make -C zigux ".len..];
        const declaration = try std.fmt.allocPrint(std.testing.allocator, "\n{s}:", .{target});
        defer std.testing.allocator.free(declaration);

        try expectContains(makefile, declaration);
    }
}

test "Phase 2 aggregate dependency shape stays explicit" {
    const allocator = std.testing.allocator;
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const validate_target = "\nphase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep\n";
    const aggregate_target = "\nphase2: phase2-validate\n";

    try expectContains(makefile, validate_target);
    try expectContains(makefile, aggregate_target);
    try expectContains(tests_readme, "`make -C zigux phase2-validate`");
    try expectContains(tests_readme, "`make -C zigux phase2`");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn closureRouteNeedle(allocator: std.mem.Allocator, route: []const u8) ![]u8 {
    if (std.mem.eql(u8, route, "make -C zigux phase2")) {
        return std.fmt.allocPrint(allocator, ",{s}`", .{route});
    }
    return std.fmt.allocPrint(allocator, "{s},", .{route});
}
