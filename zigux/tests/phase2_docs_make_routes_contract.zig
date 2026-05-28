const std = @import("std");

const phase2_make_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
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

fn makeRouteCommand(route: []const u8, buffer: []u8) ![]const u8 {
    return std.fmt.bufPrint(buffer, "make -C zigux {s}", .{route});
}

fn makeTargetDeclaration(route: []const u8, buffer: []u8) ![]const u8 {
    return std.fmt.bufPrint(buffer, "\n{s}:", .{route});
}

test "phase 2 closure note lists every shared make route once" {
    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 32 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=");
    try std.testing.expectEqual(phase2_make_routes.len, countOccurrences(closure, "make -C zigux phase2"));

    var command_buffer: [64]u8 = undefined;
    for (phase2_make_routes) |route| {
        const command = try makeRouteCommand(route, &command_buffer);
        try expectContains(closure, command);
    }

    try expectNotContains(closure, "make -C zigux phase2-shared");
    try expectNotContains(closure, "make -C zigux phase2-docs");
}

test "phase 2 closure make routes are declared by the Makefile" {
    const makefile = try readRepoFile("zigux/Makefile", 64 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectContains(makefile, ".PHONY:");

    var target_buffer: [64]u8 = undefined;
    for (phase2_make_routes) |route| {
        try expectContains(makefile, route);

        const target = try makeTargetDeclaration(route, &target_buffer);
        try expectContains(makefile, target);
    }
}

test "phase 2 aggregate route remains tied to the documented validation route" {
    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 32 * 1024);
    defer std.testing.allocator.free(closure);

    const makefile = try readRepoFile("zigux/Makefile", 64 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectContains(closure, "make -C zigux phase2-validate");
    try expectContains(closure, "make -C zigux phase2`");
    try expectContains(makefile, "\nphase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "\nphase2: phase2-validate");
}
