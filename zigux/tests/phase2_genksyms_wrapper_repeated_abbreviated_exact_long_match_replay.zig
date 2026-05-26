const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay preserves repeated abbreviated version side effects before exact long matches" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ver",
        "--dump",
        "--dump-types",
        "types.symtypes",
        "--reference",
        "foo.symref",
        "--preserve",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 2), request.version_count);
                try std.testing.expect(request.dump_defs);
                try std.testing.expect(request.preserve);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("foo.symref", request.reference_files[0]);
                try std.testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try std.testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "phase2 genksyms wrapper replay preserves repeated abbreviated version side effects before exact inline and standalone long matches" {
    var arena_state = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ver",
        "--debug",
        "--reference=bar.symref",
        "--dump",
        "--dump-types=inline.symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try std.testing.expectEqual(@as(usize, 2), request.version_count);
                try std.testing.expectEqual(@as(usize, 1), request.debug_level);
                try std.testing.expect(request.dump_defs);
                try std.testing.expectEqual(@as(usize, 1), request.reference_files.len);
                try std.testing.expectEqualStrings("bar.symref", request.reference_files[0]);
                try std.testing.expectEqualStrings("inline.symtypes", request.dump_types_file.?);
                try std.testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
