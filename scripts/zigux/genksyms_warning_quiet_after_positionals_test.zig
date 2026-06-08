const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "warning and quiet long options after positionals keep last state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "alpha.c",
        "--warnings",
        "beta.c",
        "--quiet",
        "--version",
        "--warn",
        "gamma.c",
        "--qui",
        "--warnings",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &.{
                    "--warnings",
                    "--quiet",
                    "--version",
                    "--warn",
                    "--qui",
                    "--warnings",
                    "alpha.c",
                    "beta.c",
                    "gamma.c",
                }, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "warning quiet parser matrix renders bridge json after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "--warnings",
        "middle.c",
        "--quiet",
        "-w",
        "right.c",
        "-q",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(!request.warnings);
                try testing.expectEqualSlices([]const u8, &.{
                    "--warnings",
                    "--quiet",
                    "-w",
                    "-q",
                    "left.c",
                    "middle.c",
                    "right.c",
                }, request.rendered_args);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--warnings\",\"--quiet\",\"-w\",\"-q\",\"left.c\",\"middle.c\",\"right.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "warning quiet failure preserves prior version side effects" {
    const args = [_][]const u8{
        "input.c",
        "--warnings",
        "-V",
        "--quiet",
        "--warn=extra",
    };

    const outcome = try genksyms.parseArgs(testing.allocator, &args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(@as(usize, 1), failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings("--warnings", option),
                else => return error.UnexpectedParseFailure,
            }
        },
        else => return error.ExpectedFailure,
    }
}
