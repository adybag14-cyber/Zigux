const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms");

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| return request,
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.ExpectedRequestCommand,
    }
}

fn expectRenderedArgs(request: genksyms.Request, expected: []const []const u8) !void {
    try testing.expectEqual(expected.len, request.rendered_args.len);
    for (expected, 0..) |arg, index| {
        try testing.expectEqualStrings(arg, request.rendered_args[index]);
    }
}

test "version side effect survives explicit terminator before option-looking data" {
    const args = [_][]const u8{
        "--version",
        "--",
        "--debug",
        "-r",
        "tail.symref",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.reference_files);
    defer testing.allocator.free(request.rendered_args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try expectRenderedArgs(request, &.{
        "--version",
        "--",
        "--debug",
        "-r",
        "tail.symref",
    });
}

test "short version cluster survives explicit terminator after delayed positional data" {
    const args = [_][]const u8{
        "leftover.c",
        "-VV",
        "--",
        "--reference",
        "not-a-reference.symref",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.reference_files);
    defer testing.allocator.free(request.rendered_args);

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try expectRenderedArgs(request, &.{
        "-VV",
        "leftover.c",
        "--",
        "--reference",
        "not-a-reference.symref",
    });
}

test "terminator makes pure version prefix a request rather than version command" {
    const args = [_][]const u8{
        "--ver",
        "--",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.reference_files);
    defer testing.allocator.free(request.rendered_args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try expectRenderedArgs(request, &.{ "--ver", "--" });
}
