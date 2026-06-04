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

test "version side effect keeps dash-prefixed long option arguments as data" {
    const args = [_][]const u8{
        "--version",
        "--reference",
        "--debug",
        "--dump-types",
        "--types",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.reference_files);
    defer testing.allocator.free(request.rendered_args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--debug", request.reference_files[0]);
    try testing.expectEqualStrings("--types", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "version side effect keeps dash-prefixed short option arguments as data" {
    const args = [_][]const u8{
        "-V",
        "-r",
        "-d",
        "-T",
        "--symtypes",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.reference_files);
    defer testing.allocator.free(request.rendered_args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-d", request.reference_files[0]);
    try testing.expectEqualStrings("--symtypes", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}
