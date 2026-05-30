const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectHelpCommand(outcome: genksyms.ParseOutcome, expected_versions: usize) !void {
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try testing.expectEqual(expected_versions, version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "genksyms wrapper preserves clustered short version before short help" {
    const args = [_][]const u8{"-Vh"};

    try expectHelpCommand(
        try genksyms.parseArgs(testing.allocator, &args),
        1,
    );
}

test "genksyms wrapper preserves repeated clustered short versions before short help" {
    const args = [_][]const u8{"-VVh"};

    try expectHelpCommand(
        try genksyms.parseArgs(testing.allocator, &args),
        2,
    );
}

test "genksyms wrapper stops at clustered short help before later request args" {
    const args = [_][]const u8{
        "-VVh",
        "--reference",
        "ignored.symref",
    };

    try expectHelpCommand(
        try genksyms.parseArgs(testing.allocator, &args),
        2,
    );
}
