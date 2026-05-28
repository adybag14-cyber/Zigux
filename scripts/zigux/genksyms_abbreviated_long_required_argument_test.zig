const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge accepts abbreviated long required arguments" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ref=inline.symref",
        "--refer",
        "separate.symref",
        "--dump-t=inline.symtypes",
        "--dump-ty",
        "separate.symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.reference_files.len);
                try testing.expectEqualStrings("inline.symref", request.reference_files[0]);
                try testing.expectEqualStrings("separate.symref", request.reference_files[1]);
                try testing.expectEqualStrings("separate.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
