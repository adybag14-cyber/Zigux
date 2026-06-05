const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "dump and preserve options remain active after delayed positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first-positional.c",
        "--dump",
        "middle-positional.h",
        "-p",
        "-D",
        "--preserve",
        "--reference",
        "live.symref",
        "--dump-types",
        "types.symtypes",
        "--version",
        "last-positional.S",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("live.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);

                const expected_rendered = [_][]const u8{
                    "--dump",
                    "-p",
                    "-D",
                    "--preserve",
                    "--reference",
                    "live.symref",
                    "--dump-types",
                    "types.symtypes",
                    "--version",
                    "first-positional.c",
                    "middle-positional.h",
                    "last-positional.S",
                };
                try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "bridge JSON renders dump and preserve state after positional shuffle" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "left.c",
        "--dump",
        "-p",
        "--reference",
        "refs/live.sym",
        "--dump-types",
        "types/live.symtypes",
        "right.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--dump\",\"-p\",\"--reference\",\"refs/live.sym\",\"--dump-types\",\"types/live.symtypes\",\"left.c\",\"right.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":true,\"preserve\":true,\"reference_files\":[\"refs/live.sym\"],\"dump_types_file\":\"types/live.symtypes\"}}\n",
        output.written(),
    );
}
