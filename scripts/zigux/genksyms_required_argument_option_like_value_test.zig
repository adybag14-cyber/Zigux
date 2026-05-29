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

test "genksyms consumes long option-like tokens as long required argument data" {
    const args = [_][]const u8{
        "--reference",
        "--version",
        "--dump-types",
        "--help",
        "--debug",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--version", request.reference_files[0]);
    try testing.expectEqualStrings("--help", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "genksyms consumes short option-like tokens as short required argument data" {
    const args = [_][]const u8{
        "-r",
        "-V",
        "-T",
        "-h",
        "-d",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-V", request.reference_files[0]);
    try testing.expectEqualStrings("-h", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}

test "genksyms resumes parsing after required argument consumes option-like data" {
    const args = [_][]const u8{
        "--reference",
        "-V",
        "--version",
        "-T--help",
        "--warnings",
        "-q",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expect(!request.warnings);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-V", request.reference_files[0]);
    try testing.expectEqualStrings("--help", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}
