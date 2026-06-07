const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRequest(allocator: std.mem.Allocator, args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        else => error.ExpectedRequestCommand,
    };
}

test "versioned short state clusters after positionals stay request flags" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "-VwdDp",
        "right.c",
        "-qVd",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 2), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
    try testing.expectEqualStrings("-VwdDp", request.rendered_args[0]);
    try testing.expectEqualStrings("-qVd", request.rendered_args[1]);
    try testing.expectEqualStrings("left.c", request.rendered_args[2]);
    try testing.expectEqualStrings("right.c", request.rendered_args[3]);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VwdDp\",\"-qVd\",\"left.c\",\"right.c\"],\"options\":{\"debug_level\":2,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}

test "versioned state clusters before and after required values keep normalized order" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "before.c",
        "-Vw",
        "-r",
        "ref.symref",
        "between.c",
        "-VDp",
        "-T",
        "types.symtypes",
        "-q",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(request.dump_defs);
    try testing.expect(request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("ref.symref", request.reference_files[0]);
    try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 9), request.rendered_args.len);
    try testing.expectEqualStrings("-Vw", request.rendered_args[0]);
    try testing.expectEqualStrings("-r", request.rendered_args[1]);
    try testing.expectEqualStrings("ref.symref", request.rendered_args[2]);
    try testing.expectEqualStrings("-VDp", request.rendered_args[3]);
    try testing.expectEqualStrings("-T", request.rendered_args[4]);
    try testing.expectEqualStrings("types.symtypes", request.rendered_args[5]);
    try testing.expectEqualStrings("-q", request.rendered_args[6]);
    try testing.expectEqualStrings("before.c", request.rendered_args[7]);
    try testing.expectEqualStrings("between.c", request.rendered_args[8]);
}

test "invalid tail after versioned state cluster preserves side effects" {
    const args = [_][]const u8{
        "left.c",
        "-VwDx",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings("x", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
