const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "abbreviated inline required arguments resume before terminator tail" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ref=alpha.symref",
        "--dump-t=types\nfile.symtypes",
        "--ver",
        "early.c",
        "-d",
        "--",
        "--ref=tail.symref",
        "--dump-t=tail.symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("alpha.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types\nfile.symtypes", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 8), request.rendered_args.len);
                try testing.expectEqualStrings("--ref=alpha.symref", request.rendered_args[0]);
                try testing.expectEqualStrings("--dump-t=types\nfile.symtypes", request.rendered_args[1]);
                try testing.expectEqualStrings("--ver", request.rendered_args[2]);
                try testing.expectEqualStrings("-d", request.rendered_args[3]);
                try testing.expectEqualStrings("--", request.rendered_args[4]);
                try testing.expectEqualStrings("early.c", request.rendered_args[5]);
                try testing.expectEqualStrings("--ref=tail.symref", request.rendered_args[6]);
                try testing.expectEqualStrings("--dump-t=tail.symtypes", request.rendered_args[7]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "abbreviated inline required argument tail renders escaped JSON" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ref=alpha.symref",
        "--dump-t=types\nfile.symtypes",
        "--ver",
        "early.c",
        "-d",
        "--",
        "--ref=tail.symref",
        "--dump-t=tail.symtypes",
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
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--ref=alpha.symref\",\"--dump-t=types\\nfile.symtypes\",\"--ver\",\"-d\",\"--\",\"early.c\",\"--ref=tail.symref\",\"--dump-t=tail.symtypes\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"alpha.symref\"],\"dump_types_file\":\"types\\nfile.symtypes\"}}\n",
        output.written(),
    );
}
