const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge preserves reference order with dump and preserve flags" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--reference",
        "base.symref",
        "--dump",
        "--preserve",
        "-r",
        "override.symref",
        "-D",
        "-p",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 2), request.reference_files.len);
                try testing.expectEqualStrings("base.symref", request.reference_files[0]);
                try testing.expectEqualStrings("override.symref", request.reference_files[1]);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge keeps positional references delayed after parsed options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "--reference=first.symref",
        "middle.h",
        "-rsecond.symref",
        "--preserve",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 2), request.reference_files.len);
                try testing.expectEqualStrings("first.symref", request.reference_files[0]);
                try testing.expectEqualStrings("second.symref", request.reference_files[1]);
                try testing.expectEqual(@as(usize, 5), request.rendered_args.len);
                try testing.expectEqualStrings("--reference=first.symref", request.rendered_args[0]);
                try testing.expectEqualStrings("-rsecond.symref", request.rendered_args[1]);
                try testing.expectEqualStrings("--preserve", request.rendered_args[2]);
                try testing.expectEqualStrings("leftover.c", request.rendered_args[3]);
                try testing.expectEqualStrings("middle.h", request.rendered_args[4]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms bridge leaves reference-looking tokens after terminator as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-r",
        "live.symref",
        "--",
        "-r",
        "tail.symref",
        "--reference=tail2.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("live.symref", request.reference_files[0]);
                try testing.expectEqual(@as(usize, 6), request.rendered_args.len);
                try testing.expectEqualStrings("-r", request.rendered_args[0]);
                try testing.expectEqualStrings("live.symref", request.rendered_args[1]);
                try testing.expectEqualStrings("--", request.rendered_args[2]);
                try testing.expectEqualStrings("-r", request.rendered_args[3]);
                try testing.expectEqualStrings("tail.symref", request.rendered_args[4]);
                try testing.expectEqualStrings("--reference=tail2.symref", request.rendered_args[5]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
