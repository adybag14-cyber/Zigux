const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

test "phase2 genksyms wrapper keeps repeated version counts before short option arguments used as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-V",
        "--version",
        "--ver",
        "-r",
        "-d",
        "-T",
        "--symtypes",
        "-w",
        "tail.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 3), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(request.warnings);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("-d", request.reference_files[0]);
                try testing.expectEqualStrings("--symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper keeps repeated version counts while mixing short and long option arguments used as data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "-VV",
        "--reference",
        "--debug",
        "-T",
        "-w",
        "--quiet",
        "tail.c",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 3), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("--debug", request.reference_files[0]);
                try testing.expectEqualStrings("-w", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
