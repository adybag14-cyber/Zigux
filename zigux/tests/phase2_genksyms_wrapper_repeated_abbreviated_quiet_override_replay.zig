const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay preserves repeated abbreviated version side effects before long quiet override" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ver",
        "--warnings",
        "--quiet",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 2), request.version_count);
                try std.testing.expect(!request.warnings);
                try std.testing.expectEqual(@as(usize, 0), request.debug_level);
                try std.testing.expect(!request.dump_defs);
                try std.testing.expect(!request.preserve);
                try std.testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try std.testing.expect(request.dump_types_file == null);
                try std.testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay preserves repeated abbreviated version side effects before short quiet override" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "-V",
        "-w",
        "-q",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 2), request.version_count);
                try std.testing.expect(!request.warnings);
                try std.testing.expectEqual(@as(usize, 0), request.debug_level);
                try std.testing.expect(!request.dump_defs);
                try std.testing.expect(!request.preserve);
                try std.testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try std.testing.expect(request.dump_types_file == null);
                try std.testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
