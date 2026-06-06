const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms keeps empty tokens around terminator after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "",
        "-d",
        "left.c",
        "--",
        "",
        "--help",
        "",
        "-rpost.symref",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);

                const expected_rendered = [_][]const u8{
                    "-d",
                    "",
                    "left.c",
                    "--",
                    "",
                    "--help",
                    "",
                    "-rpost.symref",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-d\",\"\",\"left.c\",\"--\",\"\",\"--help\",\"\",\"-rpost.symref\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms empty positional blocks pure version promotion before terminator" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "",
        "--version",
        "--",
        "",
        "-V",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);

                const expected_rendered = [_][]const u8{
                    "--version",
                    "",
                    "--",
                    "",
                    "-V",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            .version => return error.UnexpectedVersionCommand,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
