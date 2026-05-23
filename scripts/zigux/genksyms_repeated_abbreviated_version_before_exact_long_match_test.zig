const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "repeated abbreviated version survives before exact dump and preserve matches" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ver",
        "--dump",
        "--preserve",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(request.dump_defs);
                try testing.expect(request.preserve);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "mixed abbreviated version survives before exact dump-types and reference matches" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "-V",
        "--dump-types",
        "types.symtypes",
        "--reference",
        "foo.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expect(!request.warnings);
                try testing.expect(!request.dump_defs);
                try testing.expect(!request.preserve);
                try testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
