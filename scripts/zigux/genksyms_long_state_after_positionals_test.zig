const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "long state toggles after positionals normalize before delayed inputs" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "module.c",
        "--debug",
        "--warnings",
        "late.h",
        "--quiet",
        "--dump",
        "--preserve",
    };
    const request = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (request) {
        .command => |command| switch (command) {
            .request => |parsed| {
                try testing.expectEqual(@as(usize, 1), parsed.debug_level);
                try testing.expect(!parsed.warnings);
                try testing.expect(parsed.dump_defs);
                try testing.expect(parsed.preserve);
                try testing.expectEqual(@as(usize, 0), parsed.reference_files.len);
                try testing.expect(parsed.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, parsed.raw_args);
                try testing.expectEqualSlices([]const u8, &.{
                    "--debug",
                    "--warnings",
                    "--quiet",
                    "--dump",
                    "--preserve",
                    "module.c",
                    "late.h",
                }, parsed.rendered_args);

                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();
                try genksyms.renderGenksymsBridge(&output.writer, parsed);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--debug\",\"--warnings\",\"--quiet\",\"--dump\",\"--preserve\",\"module.c\",\"late.h\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "abbreviated long state toggles after positionals keep canonical state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.c",
        "--deb",
        "--warn",
        "middle.h",
        "--qui",
        "--pre",
        "last.S",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &.{
                    "--deb",
                    "--warn",
                    "--qui",
                    "--pre",
                    "first.c",
                    "middle.h",
                    "last.S",
                }, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "inline values on long state toggles after positionals fail canonically" {
    const cases = [_]struct {
        argv: []const []const u8,
        expected_option: []const u8,
        expected_versions: usize,
    }{
        .{
            .argv = &.{ "pre.c", "--version", "--debug=2" },
            .expected_option = "--debug",
            .expected_versions = 1,
        },
        .{
            .argv = &.{ "pre.c", "--ver", "--warnings=yes" },
            .expected_option = "--warnings",
            .expected_versions = 1,
        },
        .{
            .argv = &.{ "pre.c", "--quiet=no" },
            .expected_option = "--quiet",
            .expected_versions = 0,
        },
        .{
            .argv = &.{ "pre.c", "--dump=defs" },
            .expected_option = "--dump",
            .expected_versions = 0,
        },
        .{
            .argv = &.{ "pre.c", "--preserve=yes" },
            .expected_option = "--preserve",
            .expected_versions = 0,
        },
    };

    for (cases) |case| {
        const outcome = try genksyms.parseArgs(testing.allocator, case.argv);
        switch (outcome) {
            .failure => |failure| {
                try testing.expectEqual(case.expected_versions, failure.version_count);
                switch (failure.reason) {
                    .unexpected_option_argument => |option| {
                        try testing.expectEqualStrings(case.expected_option, option);
                    },
                    else => return error.UnexpectedParseFailure,
                }
            },
            else => return error.ExpectedFailure,
        }
    }
}
