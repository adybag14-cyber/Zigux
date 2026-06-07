const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectEmptyLongOptionAmbiguous(args: []const []const u8, expected_versions: usize) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .ambiguous_option => |option| try testing.expectEqualStrings("--", option),
                else => return error.ExpectedAmbiguousEmptyLongOption,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "genksyms empty long option name after positionals canonicalizes as ambiguous" {
    const args = [_][]const u8{
        "-V",
        "leftover.c",
        "-r",
        "ref.sym",
        "--=value",
    };

    try expectEmptyLongOptionAmbiguous(&args, 1);
}

test "genksyms empty long option with empty value after positionals stays ambiguous" {
    const args = [_][]const u8{
        "leftover.c",
        "--debug",
        "--=",
    };

    try expectEmptyLongOptionAmbiguous(&args, 0);
}

test "genksyms empty long option after terminator remains argv data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "leftover.c",
        "-r",
        "ref.sym",
        "--",
        "--=value",
        "--=",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("ref.sym", request.reference_files[0]);
                try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
                try testing.expectEqualStrings("-V", request.rendered_args[0]);
                try testing.expectEqualStrings("-r", request.rendered_args[1]);
                try testing.expectEqualStrings("ref.sym", request.rendered_args[2]);
                try testing.expectEqualStrings("leftover.c", request.rendered_args[3]);
                try testing.expectEqualStrings("--", request.rendered_args[4]);
                try testing.expectEqualStrings("--=value", request.rendered_args[5]);
                try testing.expectEqualStrings("--=", request.rendered_args[6]);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expect(std.mem.indexOf(u8, output.written(), "\"--=value\",\"--=\"") != null);
                try testing.expect(std.mem.indexOf(u8, output.written(), "\"reference_files\":[\"ref.sym\"]") != null);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
