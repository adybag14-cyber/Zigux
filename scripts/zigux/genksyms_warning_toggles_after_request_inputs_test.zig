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

test "warning toggles after positional request input keep request mode" {
    const args = [_][]const u8{
        "input.c",
        "--warnings",
        "--quiet",
        "--warnings",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expect(request.warnings);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
    try testing.expectEqualStrings("--warnings", request.rendered_args[0]);
    try testing.expectEqualStrings("--quiet", request.rendered_args[1]);
    try testing.expectEqualStrings("--warnings", request.rendered_args[2]);
    try testing.expectEqualStrings("input.c", request.rendered_args[3]);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expect(std.mem.containsAtLeast(u8, output.written(), 1, "\"warnings\":true"));
}

test "short warning and quiet cluster after lone dash updates request state" {
    const args = [_][]const u8{
        "-",
        "-wqwp",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expect(request.warnings);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 2), request.rendered_args.len);
    try testing.expectEqualStrings("-wqwp", request.rendered_args[0]);
    try testing.expectEqualStrings("-", request.rendered_args[1]);
}

test "required option data before warning toggles stays data" {
    const args = [_][]const u8{
        "--reference",
        "--warnings",
        "--quiet",
        "--dump-types",
        "-w",
        "-",
    };
    const request = try expectRequest(&args);
    defer testing.allocator.free(request.rendered_args);
    defer testing.allocator.free(request.reference_files);

    try testing.expect(!request.warnings);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("--warnings", request.reference_files[0]);
    try testing.expectEqualStrings("-w", request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
}
