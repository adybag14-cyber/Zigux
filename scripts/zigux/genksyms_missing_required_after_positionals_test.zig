const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectMissingArgumentFailure(
    args: []const []const u8,
    expected_option: []const u8,
    expected_version_count: usize,
) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_version_count, failure.version_count);
            switch (failure.reason) {
                .missing_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedMissingArgumentFailure,
            }
        },
        else => return error.ExpectedMissingArgumentFailure,
    }
}

test "genksyms missing long required argument still fires after delayed positionals" {
    const args = [_][]const u8{
        "--version",
        "prelude.c",
        "-d",
        "middle.o",
        "--reference",
    };

    try expectMissingArgumentFailure(&args, "--reference", 1);
}

test "genksyms missing long dump-types argument preserves version after delayed positionals" {
    const args = [_][]const u8{
        "prelude.c",
        "--ver",
        "middle.o",
        "--dump-types",
    };

    try expectMissingArgumentFailure(&args, "--dump-types", 1);
}

test "genksyms missing short reference argument preserves clustered versions after positionals" {
    const args = [_][]const u8{
        "-VV",
        "input.c",
        "--warnings",
        "tail.sym",
        "-r",
    };

    try expectMissingArgumentFailure(&args, "r", 2);
}

test "genksyms missing short required argument preserves clustered versions after positionals" {
    const args = [_][]const u8{
        "-VV",
        "input.c",
        "--warnings",
        "tail.sym",
        "-T",
    };

    try expectMissingArgumentFailure(&args, "T", 2);
}
