const std = @import("std");

const phase2_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
    "phase2",
};

test "phase2 closure note, makefile, and workflow keep the same route order" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure_note);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    var closure_cursor: usize = 0;
    var make_cursor: usize = 0;
    var workflow_cursor: usize = 0;

    for (phase2_routes) |route| {
        const command = try std.fmt.allocPrint(std.testing.allocator, "make -C zigux {s}", .{route});
        defer std.testing.allocator.free(command);

        const closure_index = findAfter(closure_note, command, closure_cursor);
        closure_cursor = closure_index + command.len;

        const make_target = try std.fmt.allocPrint(std.testing.allocator, "{s}:", .{route});
        defer std.testing.allocator.free(make_target);
        const make_index = findLineAfter(makefile, make_target, make_cursor);
        make_cursor = make_index + make_target.len;

        const workflow_index = findAfter(workflow, command, workflow_cursor);
        workflow_cursor = workflow_index + command.len;
    }
}

test "phase2 aggregate route stays closed through the validator target" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure_note);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");
    try expectContains(makefile, "\nphase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "\nphase2: phase2-validate");
    try expectContains(workflow, "python3 scripts/zigux/validate-phase2.py");
    try expectContains(workflow, "python3 scripts/zigux/validate-phase2-closure.py --self-test");
    try expectContains(workflow, "python3 scripts/zigux/validate-phase2-closure.py");

    const make_validate = findAfter(makefile, "\nphase2-validate:", 0);
    const make_aggregate = findAfter(makefile, "\nphase2: phase2-validate", make_validate);
    try std.testing.expect(make_aggregate > make_validate);

    const workflow_validate = findAfter(workflow, "make -C zigux phase2-validate", 0);
    const workflow_aggregate = findAfter(workflow, "make -C zigux phase2", workflow_validate + "make -C zigux phase2-validate".len);
    try std.testing.expect(workflow_aggregate > workflow_validate);
}

test "phase2 closure route roster is exactly the shipped eight-route packet" {
    const allocator = std.testing.allocator;
    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure_note);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const shared_line =
        "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2";

    try expectContains(closure_note, shared_line);

    for (phase2_routes) |route| {
        const target = try std.fmt.allocPrint(std.testing.allocator, "{s}:", .{route});
        defer std.testing.allocator.free(target);
        try std.testing.expectEqual(@as(usize, 1), countLineOccurrences(makefile, target));
    }
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn findAfter(haystack: []const u8, needle: []const u8, start: usize) usize {
    return std.mem.indexOfPos(u8, haystack, start, needle) orelse @panic("expected marker was not found in order");
}

fn findLineAfter(haystack: []const u8, needle: []const u8, start: usize) usize {
    var cursor = start;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        if (index == 0 or haystack[index - 1] == '\n') return index;
        cursor = index + needle.len;
    }
    @panic("expected line marker was not found in order");
}

fn countLineOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        if (index == 0 or haystack[index - 1] == '\n') count += 1;
        cursor = index + needle.len;
    }
    return count;
}
