const std = @import("std");

const RouteBlock = struct {
    header: []const u8,
    body: []const u8,
};

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn findRouteBlock(makefile: []const u8, route: []const u8) !RouteBlock {
    const route_header = try std.fmt.allocPrint(std.testing.allocator, "\n{s}:", .{route});
    defer std.testing.allocator.free(route_header);

    const route_start = std.mem.indexOf(u8, makefile, route_header) orelse return error.MissingRoute;
    const header_start = route_start + 1;
    const body_start = std.mem.indexOfScalarPos(u8, makefile, header_start, '\n') orelse return error.MissingRouteBody;
    const next_route = std.mem.indexOf(u8, makefile[body_start + 1 ..], "\nphase") orelse makefile.len - body_start - 1;
    const body_end = body_start + 1 + next_route;

    return .{
        .header = makefile[header_start .. body_start - 1],
        .body = makefile[body_start + 1 .. body_end],
    };
}

fn expectCommandOnce(haystack: []const u8, command: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        const trimmed = std.mem.trim(u8, line, "\t ");
        if (std.mem.eql(u8, trimmed, command)) count += 1;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn commandLineIndex(haystack: []const u8, command: []const u8) !usize {
    var line_index: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| : (line_index += 1) {
        const trimmed = std.mem.trim(u8, line, "\t ");
        if (std.mem.eql(u8, trimmed, command)) return line_index;
    }
    return error.MissingExpectedRouteStep;
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = try commandLineIndex(haystack, first);
    const second_index = try commandLineIndex(haystack, second);
    try std.testing.expect(first_index < second_index);
}

test "phase 2 cross Makefile route keeps direct checker pair wired" {
    const makefile = try readRepoFile("zigux/Makefile");
    defer std.testing.allocator.free(makefile);

    const phase2_cross = try findRouteBlock(makefile, "phase2-cross");

    try std.testing.expectEqualStrings("phase2-cross", phase2_cross.header);
    try expectCommandOnce(phase2_cross.body, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try expectCommandOnce(phase2_cross.body, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectCommandOnce(phase2_cross.body, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
    try expectCommandOnce(phase2_cross.body, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py");

    try expectBefore(
        phase2_cross.body,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    );
    try expectBefore(
        phase2_cross.body,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    );
    try expectBefore(
        phase2_cross.body,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    );

    try std.testing.expect(std.mem.indexOf(u8, phase2_cross.body, "validate-phase2.py") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase2_cross.body, "validate-phase2-closure.py") == null);

    const phase2_validate = try findRouteBlock(makefile, "phase2-validate");
    try std.testing.expect(std.mem.indexOf(u8, phase2_validate.header, "phase2-cross") != null);
}
