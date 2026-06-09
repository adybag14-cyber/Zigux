const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "underscore-prefixed positionals remain delayed argv data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "_lead.c",
        "--debug",
        "_middle.h",
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
                try testing.expectEqualStrings("_lead.c", request.rendered_args[2]);
                try testing.expectEqualStrings("_middle.h", request.rendered_args[3]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "underscore-prefixed required values are consumed as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "unit.c",
        "--reference",
        "_baseline.symref",
        "-T_types.symtypes",
        "_after.c",
        "-p",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("_baseline.symref", request.reference_files[0]);
                try testing.expectEqualStrings("_types.symtypes", request.dump_types_file.?);
                try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
                try testing.expectEqualStrings("--reference", request.rendered_args[0]);
                try testing.expectEqualStrings("_baseline.symref", request.rendered_args[1]);
                try testing.expectEqualStrings("-T_types.symtypes", request.rendered_args[2]);
                try testing.expectEqualStrings("-p", request.rendered_args[3]);
                try testing.expectEqualStrings("unit.c", request.rendered_args[4]);
                try testing.expectEqualStrings("_after.c", request.rendered_args[5]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "underscore-prefixed terminator tails do not change parser state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-d",
        "before.c",
        "--",
        "_tail.c",
        "-r",
        "_ignored.symref",
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
                try testing.expectEqualStrings("_tail.c", request.rendered_args[3]);
                try testing.expectEqualStrings("-r", request.rendered_args[4]);
                try testing.expectEqualStrings("_ignored.symref", request.rendered_args[5]);
                try testing.expectEqualStrings("--debug", request.rendered_args[6]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "underscore-prefixed bridge JSON preserves live rendered argv order" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "_ref.sym",
        "_unit.c",
        "--",
        "_tail.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                var output: std.Io.Writer.Allocating = .init(testing.allocator);
                defer output.deinit();

                try genksyms.renderGenksymsBridge(&output.writer, request);
                try testing.expectEqualStrings(
                    "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--reference\",\"_ref.sym\",\"_unit.c\",\"--\",\"_tail.c\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"_ref.sym\"],\"dump_types_file\":null}}\n",
                    output.written(),
                );
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
