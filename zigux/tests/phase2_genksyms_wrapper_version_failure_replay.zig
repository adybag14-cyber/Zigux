const std = @import("std");
const testing = std.testing;

const genksyms = @import("genksyms");

fn expectFailure(outcome: genksyms.ParseOutcome) !genksyms.ParsedFailure {
    return switch (outcome) {
        .failure => |failure| failure,
        else => error.ExpectedParseFailure,
    };
}

test "genksyms wrapper preserves version before invalid long option failure" {
    const args = [_][]const u8{
        "--version",
        "--unknown",
    };
    const failure = try expectFailure(try genksyms.parseArgs(testing.allocator, &args));

    try testing.expectEqual(@as(usize, 1), failure.version_count);
    switch (failure.reason) {
        .invalid_option => |option| try testing.expectEqualStrings("--unknown", option),
        else => return error.UnexpectedParseFailure,
    }
}

test "genksyms wrapper preserves repeated versions before ambiguous long option failure" {
    const args = [_][]const u8{
        "-V",
        "--ver",
        "--du",
    };
    const failure = try expectFailure(try genksyms.parseArgs(testing.allocator, &args));

    try testing.expectEqual(@as(usize, 2), failure.version_count);
    switch (failure.reason) {
        .ambiguous_option => |option| try testing.expectEqualStrings("--du", option),
        else => return error.UnexpectedParseFailure,
    }
}

test "genksyms wrapper keeps pure version command when only versions precede eof" {
    const args = [_][]const u8{
        "--version",
        "-VV",
        "--ver",
    };
    const outcome = try genksyms.parseArgs(testing.allocator, &args);

    switch (outcome) {
        .command => |command| switch (command) {
            .version => |count| try testing.expectEqual(@as(usize, 4), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}
