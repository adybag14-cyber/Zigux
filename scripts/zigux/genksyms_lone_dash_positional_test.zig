const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "genksyms treats lone dash as positional data before pure version flags" {
    const args = [_][]const u8{ "-", "-VV" };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expectEqual(@as(usize, 2), request.rendered_args.len);
    try testing.expectEqualStrings("-VV", request.rendered_args[0]);
    try testing.expectEqualStrings("-", request.rendered_args[1]);
}

test "genksyms keeps lone dash positional before explicit terminator tail" {
    const args = [_][]const u8{ "-", "-d", "--", "--version", "tail.sym" };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 5), request.rendered_args.len);
    try testing.expectEqualStrings("-d", request.rendered_args[0]);
    try testing.expectEqualStrings("-", request.rendered_args[1]);
    try testing.expectEqualStrings("--", request.rendered_args[2]);
    try testing.expectEqualStrings("--version", request.rendered_args[3]);
    try testing.expectEqualStrings("tail.sym", request.rendered_args[4]);
}

test "genksyms consumes lone dash as required option argument data" {
    const args = [_][]const u8{ "--reference", "-", "--dump-types", "-", "-w" };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-", request.reference_files[0]);
    try testing.expectEqualStrings("-", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}
