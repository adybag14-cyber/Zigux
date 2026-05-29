const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectInvalidShortFailure(outcome: genksyms.ParseOutcome, expected_versions: usize, expected_option: []const u8) !void {
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .invalid_option => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedInvalidShortFailure,
            }
        },
        else => return error.ExpectedInvalidShortFailure,
    }
}

test "genksyms wrapper preserves long version before invalid short option" {
    const args = [_][]const u8{
        "--version",
        "-x",
    };

    try expectInvalidShortFailure(
        try genksyms.parseArgs(testing.allocator, &args),
        1,
        "x",
    );
}

test "genksyms wrapper preserves repeated mixed versions before invalid short option" {
    const args = [_][]const u8{
        "--ver",
        "-VV",
        "-Z",
    };

    try expectInvalidShortFailure(
        try genksyms.parseArgs(testing.allocator, &args),
        3,
        "Z",
    );
}

test "genksyms wrapper preserves clustered short version before later invalid short option" {
    const args = [_][]const u8{"-VVx"};

    try expectInvalidShortFailure(
        try genksyms.parseArgs(testing.allocator, &args),
        2,
        "x",
    );
}
