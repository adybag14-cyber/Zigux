const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "lone dash after delayed positionals keeps later options parsed first" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "-",
        "-d",
        "--reference",
        "ref.sym",
    };

    const request = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (request) {
        .command => |command| switch (command) {
            .request => |parsed| {
                const expected_rendered = [_][]const u8{
                    "-d",
                    "--reference",
                    "ref.sym",
                    "leftover.c",
                    "-",
                };
                try testing.expectEqual(@as(usize, 1), parsed.debug_level);
                try testing.expectEqual(@as(usize, 1), parsed.reference_files.len);
                try testing.expectEqualStrings("ref.sym", parsed.reference_files[0]);
                try testing.expectEqualSlices([]const u8, &args, parsed.raw_args);
                try testing.expectEqualSlices([]const u8, &expected_rendered, parsed.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "lone dash after positionals keeps option-like required values as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.o",
        "-",
        "--dump-types",
        "--version",
        "-r--help",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                const expected_rendered = [_][]const u8{
                    "--dump-types",
                    "--version",
                    "-r--help",
                    "first.o",
                    "-",
                };
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("--help", request.reference_files[0]);
                try testing.expectEqualStrings("--version", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 0), request.version_count);
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "lone dash after positionals renders stable bridge JSON" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.sym",
        "-",
        "-w",
        "-q",
        "-D",
        "-p",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-w\",\"-q\",\"-D\",\"-p\",\"input.sym\",\"-\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
