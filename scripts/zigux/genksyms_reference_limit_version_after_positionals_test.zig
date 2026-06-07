const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectTooManyReferences(args: []const []const u8, expected_version_count: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            try testing.expectEqual(genksyms.ParseFailure.too_many_reference_files, failure.reason);
        },
        else => return error.ExpectedTooManyReferenceFiles,
    }
}

test "genksyms bridge preserves version count before separated reference limit after positionals" {
    const args = [_][]const u8{
        "leftover.c",
        "-V",
        "--version",
        "-r",
        "01.symref",
        "-r",
        "02.symref",
        "-r",
        "03.symref",
        "-r",
        "04.symref",
        "-r",
        "05.symref",
        "-r",
        "06.symref",
        "-r",
        "07.symref",
        "-r",
        "08.symref",
        "-r",
        "09.symref",
        "-r",
        "10.symref",
        "-r",
        "11.symref",
        "-r",
        "12.symref",
        "-r",
        "13.symref",
        "-r",
        "14.symref",
        "-r",
        "15.symref",
        "-r",
        "16.symref",
        "-r",
        "17.symref",
    };

    try expectTooManyReferences(&args, 2);
}

test "genksyms bridge preserves version count before inline reference limit after positionals" {
    const args = [_][]const u8{
        "leftover.c",
        "--ver",
        "--reference=01.symref",
        "--reference=02.symref",
        "--reference=03.symref",
        "--reference=04.symref",
        "--reference=05.symref",
        "--reference=06.symref",
        "--reference=07.symref",
        "--reference=08.symref",
        "--reference=09.symref",
        "--reference=10.symref",
        "--reference=11.symref",
        "--reference=12.symref",
        "--reference=13.symref",
        "--reference=14.symref",
        "--reference=15.symref",
        "--reference=16.symref",
        "--reference=17.symref",
    };

    try expectTooManyReferences(&args, 1);
}

test "genksyms bridge accepts sixteen references with delayed positionals and versions" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "-V",
        "--version",
        "--reference=01.symref",
        "--reference=02.symref",
        "--reference=03.symref",
        "--reference=04.symref",
        "--reference=05.symref",
        "--reference=06.symref",
        "--reference=07.symref",
        "--reference=08.symref",
        "--reference=09.symref",
        "--reference=10.symref",
        "--reference=11.symref",
        "--reference=12.symref",
        "--reference=13.symref",
        "--reference=14.symref",
        "--reference=15.symref",
        "--reference=16.symref",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 2), request.version_count);
                try testing.expectEqual(@as(usize, 16), request.reference_files.len);
                try testing.expectEqualStrings("01.symref", request.reference_files[0]);
                try testing.expectEqualStrings("16.symref", request.reference_files[15]);
                try testing.expectEqual(@as(usize, args.len), request.rendered_args.len);
                try testing.expectEqualStrings("-V", request.rendered_args[0]);
                try testing.expectEqualStrings("--version", request.rendered_args[1]);
                try testing.expectEqualStrings("--reference=01.symref", request.rendered_args[2]);
                try testing.expectEqualStrings("leftover.c", request.rendered_args[18]);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}
