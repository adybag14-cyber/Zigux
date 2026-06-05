const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms.zig");

fn expectMissingRequiredAfterRequest(
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
                else => return error.ExpectedMissingOptionArgument,
            }
        },
        else => return error.ExpectedFailure,
    }
}

test "genksyms missing long reference after request input keeps version side effect" {
    const args = [_][]const u8{
        "leftover.c",
        "--version",
        "--reference",
    };

    try expectMissingRequiredAfterRequest(&args, "--reference", 1);
}

test "genksyms missing abbreviated dump-types after required data keeps data opaque" {
    const args = [_][]const u8{
        "--reference",
        "--version",
        "--ver",
        "--dump-t",
    };

    try expectMissingRequiredAfterRequest(&args, "--dump-types", 1);
}

test "genksyms missing short dump-types after stdin request input reports short option" {
    const args = [_][]const u8{
        "-",
        "-V",
        "-T",
    };

    try expectMissingRequiredAfterRequest(&args, "T", 1);
}
