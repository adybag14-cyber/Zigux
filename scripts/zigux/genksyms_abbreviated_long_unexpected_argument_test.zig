const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectUnexpectedInlineArgument(args: []const []const u8, expected_option: []const u8, expected_versions: usize) !void {
    const outcome = try genksyms.parseArgs(testing.allocator, args);
    switch (outcome) {
        .failure => |failure| {
            try testing.expectEqual(expected_versions, failure.version_count);
            switch (failure.reason) {
                .unexpected_option_argument => |option| try testing.expectEqualStrings(expected_option, option),
                else => return error.ExpectedUnexpectedOptionArgument,
            }
        },
        else => return error.ExpectedParseFailure,
    }
}

test "genksyms rejects inline arguments for abbreviated long command options" {
    const help_args = [_][]const u8{"--hel=topic"};
    try expectUnexpectedInlineArgument(&help_args, "--help", 0);

    const version_args = [_][]const u8{"--ver=1"};
    try expectUnexpectedInlineArgument(&version_args, "--version", 0);
}

test "genksyms rejects inline arguments for abbreviated long flag options" {
    const debug_args = [_][]const u8{"--deb=2"};
    try expectUnexpectedInlineArgument(&debug_args, "--debug", 0);

    const warnings_args = [_][]const u8{"--warn=yes"};
    try expectUnexpectedInlineArgument(&warnings_args, "--warnings", 0);

    const quiet_args = [_][]const u8{"--qui=no"};
    try expectUnexpectedInlineArgument(&quiet_args, "--quiet", 0);

    const preserve_args = [_][]const u8{"--pres=keep"};
    try expectUnexpectedInlineArgument(&preserve_args, "--preserve", 0);
}

test "genksyms keeps exact dump separate from abbreviated dump-types inline values" {
    const dump_args = [_][]const u8{"--dump=defs"};
    try expectUnexpectedInlineArgument(&dump_args, "--dump", 0);

    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const dump_types_args = [_][]const u8{"--dump-t=types.symtypes"};
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &dump_types_args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expect(!request.dump_defs);
                try testing.expectEqualStrings("types.symtypes", request.dump_types_file.?);
                try testing.expectEqualSlices([]const u8, &dump_types_args, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "genksyms preserves version side effects before abbreviated long unexpected arguments" {
    const debug_args = [_][]const u8{
        "--ver",
        "--deb=2",
    };
    try expectUnexpectedInlineArgument(&debug_args, "--debug", 1);

    const help_args = [_][]const u8{
        "--version",
        "--hel=topic",
    };
    try expectUnexpectedInlineArgument(&help_args, "--help", 1);
}
