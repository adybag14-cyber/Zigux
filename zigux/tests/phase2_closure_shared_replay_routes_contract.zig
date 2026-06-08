const std = @import("std");

const closure_path = "Documentation/zigux/phase2-closure.md";

const make_routes_marker =
    "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2";

const validators_marker =
    "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py";

test "phase2 closure shared replay routes block remains explicit and parked" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();

    const closure = try readClosure(arena.allocator());

    try expectContains(closure, "## Shared Replay Routes");
    try expectContains(closure, make_routes_marker);
    try expectContains(closure, validators_marker);
    try expectContains(closure, "## Repo-Reality Gaps");
    try expectOrdered(closure, "## Current Shared Repo-Tooling Evidence", "## Shared Replay Routes");
    try expectOrdered(closure, "## Shared Replay Routes", "## Repo-Reality Gaps");
    try expectOrdered(closure, "PHASE2_STATUS=parked", "## Shared Replay Routes");
}

test "phase2 closure make route list preserves the aggregate route handoff" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();

    const closure = try readClosure(arena.allocator());
    const marker = try extractMarker(closure, "PHASE2_SHARED_MAKE_ROUTES=");
    const routes = try splitCsv(arena.allocator(), marker["PHASE2_SHARED_MAKE_ROUTES=".len..]);

    try std.testing.expectEqual(@as(usize, 8), routes.len);
    try std.testing.expectEqualStrings("make -C zigux phase2-toolchain", routes[0]);
    try std.testing.expectEqualStrings("make -C zigux phase2-tools", routes[1]);
    try std.testing.expectEqualStrings("make -C zigux phase2-kconfig", routes[2]);
    try std.testing.expectEqualStrings("make -C zigux phase2-cross", routes[3]);
    try std.testing.expectEqualStrings("make -C zigux phase2-genksyms", routes[4]);
    try std.testing.expectEqualStrings("make -C zigux phase2-fixdep", routes[5]);
    try std.testing.expectEqualStrings("make -C zigux phase2-validate", routes[6]);
    try std.testing.expectEqualStrings("make -C zigux phase2", routes[7]);
}

test "phase2 closure validators keep aggregate before closure-specific validation" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();

    const closure = try readClosure(arena.allocator());
    const marker = try extractMarker(closure, "PHASE2_CLOSURE_VALIDATORS=");
    const validators = try splitCsv(arena.allocator(), marker["PHASE2_CLOSURE_VALIDATORS=".len..]);

    try std.testing.expectEqual(@as(usize, 2), validators.len);
    try std.testing.expectEqualStrings("python3 scripts/zigux/validate-phase2.py", validators[0]);
    try std.testing.expectEqualStrings("python3 scripts/zigux/validate-phase2-closure.py", validators[1]);
    try expectOrdered(closure, "shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`", validators_marker);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readClosure(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, closure_path, allocator, .limited(256 * 1024));
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn extractMarker(text: []const u8, prefix: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, text, prefix) orelse return error.MissingMarker;
    const end = std.mem.indexOfScalarPos(u8, text, start, '\n') orelse text.len;
    return std.mem.trim(u8, text[start..end], "- `");
}

fn splitCsv(allocator: std.mem.Allocator, text: []const u8) ![][]const u8 {
    var count: usize = 1;
    for (text) |byte| {
        if (byte == ',') count += 1;
    }

    const parts = try allocator.alloc([]const u8, count);
    var it = std.mem.splitScalar(u8, text, ',');
    var index: usize = 0;
    while (it.next()) |raw| {
        parts[index] = std.mem.trim(u8, raw, " `");
        index += 1;
    }
    try std.testing.expectEqual(count, index);
    return parts;
}
