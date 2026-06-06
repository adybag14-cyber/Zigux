const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "repeated warning and quiet toggles after positionals keep the last state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "module.sym",
        "--warnings",
        "--quiet",
        "--warnings",
        "-q",
        "-w",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                const expected_rendered = [_][]const u8{
                    "--warnings",
                    "--quiet",
                    "--warnings",
                    "-q",
                    "-w",
                    "module.sym",
                };

                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqual(@as(usize, 0), request.version_count);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "bridge output reflects repeated warning and quiet toggle normalization" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.sym",
        "--warnings",
        "-q",
        "--warn",
        "--quiet",
        "last.sym",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(!request.warnings);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--warnings\",\"-q\",\"--warn\",\"--quiet\",\"first.sym\",\"last.sym\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
