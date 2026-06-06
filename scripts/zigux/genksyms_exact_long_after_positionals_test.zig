const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

test "exact long dump stays distinct from dump-types after positionals" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "--dump",
        "--dump-types=types.symtypes",
        "--dump-t",
        "override.symtypes",
        "rightover.h",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);

    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.dump_defs);
                try testing.expectEqualStrings("override.symtypes", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
                try testing.expectEqualStrings("--dump", request.rendered_args[0]);
                try testing.expectEqualStrings("--dump-types=types.symtypes", request.rendered_args[1]);
                try testing.expectEqualStrings("--dump-t", request.rendered_args[2]);
                try testing.expectEqualStrings("override.symtypes", request.rendered_args[3]);
                try testing.expectEqualStrings("leftover.c", request.rendered_args[4]);
                try testing.expectEqualStrings("rightover.h", request.rendered_args[5]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "bridge json preserves exact dump and dump-types disambiguation" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "--dump",
        "--dump-types=types.symtypes",
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
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--dump\",\"--dump-types=types.symtypes\",\"input.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":true,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":\"types.symtypes\"}}\n",
        output.written(),
    );
}
