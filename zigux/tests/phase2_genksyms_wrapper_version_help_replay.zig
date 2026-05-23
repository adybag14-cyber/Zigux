const std = @import("std");
const genksyms = @import("genksyms");

test "phase2 genksyms wrapper replay preserves pure version command counts across mixed short and long requests" {
    const args = [_][]const u8{
        "-V",
        "--ver",
        "-VV",
    };
    const outcome = try genksyms.parseArgs(std.testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .version => |count| try std.testing.expectEqual(@as(usize, 4), count),
            else => return error.ExpectedVersionCommand,
        },
        else => return error.ExpectedVersionCommand,
    }
}

test "phase2 genksyms wrapper replay keeps version side effect before long help" {
    const args = [_][]const u8{
        "--version",
        "--help",
    };
    const outcome = try genksyms.parseArgs(std.testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try std.testing.expectEqual(@as(usize, 1), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}

test "phase2 genksyms wrapper replay keeps mixed version side effects before short help" {
    const args = [_][]const u8{
        "--ver",
        "-VV",
        "-h",
    };
    const outcome = try genksyms.parseArgs(std.testing.allocator, &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .help => |version_count| try std.testing.expectEqual(@as(usize, 3), version_count),
            else => return error.ExpectedHelpCommand,
        },
        else => return error.ExpectedHelpCommand,
    }
}
