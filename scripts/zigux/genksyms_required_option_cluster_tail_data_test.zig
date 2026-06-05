const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "required short option cluster tails stay data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-rVdqDwp",
        "-TqDdwVr",
        "-d",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("VdqDwp", request.reference_files[0]);
                try testing.expectEqualStrings("qDdwVr", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.raw_args);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "required short option cluster tail can look like another required option" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-rTtypes.symtypes",
        "-Trr.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 0), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("Ttypes.symtypes", request.reference_files[0]);
                try testing.expectEqualStrings("rr.symref", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
