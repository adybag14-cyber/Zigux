const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "asterisk-prefixed positionals remain delayed argv data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "*lead.c",
        "--debug",
        "*middle.h",
        "-w",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try testing.expectEqualStrings("--debug", request.rendered_args[0]);
                try testing.expectEqualStrings("-w", request.rendered_args[1]);
                try testing.expectEqualStrings("*lead.c", request.rendered_args[2]);
                try testing.expectEqualStrings("*middle.h", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "asterisk-prefixed required values are consumed as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "unit.c",
        "--reference",
        "*baseline.symref",
        "-T*types.symtypes",
        "*after.c",
        "-p",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("*baseline.symref", request.reference_files[0]);
                try testing.expectEqualStrings("*types.symtypes", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
                try testing.expectEqualStrings("--reference", request.rendered_args[0]);
                try testing.expectEqualStrings("*baseline.symref", request.rendered_args[1]);
                try testing.expectEqualStrings("-T*types.symtypes", request.rendered_args[2]);
                try testing.expectEqualStrings("-p", request.rendered_args[3]);
                try testing.expectEqualStrings("unit.c", request.rendered_args[4]);
                try testing.expectEqualStrings("*after.c", request.rendered_args[5]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "asterisk-prefixed terminator tails do not change parser state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-d",
        "before.c",
        "--",
        "*tail.c",
        "-r",
        "*ignored.symref",
        "--debug",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqual(@as(usize, 7), request.rendered_args.len);
                try testing.expectEqualStrings("-d", request.rendered_args[0]);
                try testing.expectEqualStrings("before.c", request.rendered_args[1]);
                try testing.expectEqualStrings("--", request.rendered_args[2]);
                try testing.expectEqualStrings("*tail.c", request.rendered_args[3]);
                try testing.expectEqualStrings("-r", request.rendered_args[4]);
                try testing.expectEqualStrings("*ignored.symref", request.rendered_args[5]);
                try testing.expectEqualStrings("--debug", request.rendered_args[6]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "asterisk-prefixed bridge JSON preserves live rendered argv order" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "*ref.sym",
        "*unit.c",
        "--",
        "*tail.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"*ref.sym\",\"*unit.c\",\"--\",\"*tail.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"*ref.sym\"],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
