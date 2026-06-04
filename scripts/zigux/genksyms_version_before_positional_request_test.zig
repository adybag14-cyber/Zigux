const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

test "pure version flags become side effects when positional request data is present" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "leftover.c",
        "--ver",
        "-",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
                try testing.expectEqualStrings("--version", request.rendered_args[0]);
                try testing.expectEqualStrings("--ver", request.rendered_args[1]);
                try testing.expectEqualStrings("leftover.c", request.rendered_args[2]);
                try testing.expectEqualStrings("-", request.rendered_args[3]);
                try testing.expectEqual(@as(usize, 0), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
            },
            .version => return error.ExpectedRequestNotVersionCommand,
            .help => return error.ExpectedRequestNotHelpCommand,
        },
        .failure => return error.ExpectedRequestNotFailure,
    }
}
