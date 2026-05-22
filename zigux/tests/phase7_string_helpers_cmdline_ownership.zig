const std = @import("std");
const string_helpers = @import("../../lib/string_helpers.zig");

test "phase 7 string helpers cmdline ownership keeps caller storage untouched while normalizing only duplicated output" {
    const source = [_]u8{ 'z', 'i', 'g', 0, 'b', 'u', 'i', 'l', 'd', '\n', '"', 0, 0 };
    const quoted = (try string_helpers.kstrdupQuotableCmdline(std.testing.allocator, &source)).?;
    defer std.testing.allocator.free(quoted);

    try std.testing.expectEqualStrings("zig build\\x0A\\x22", quoted);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'z', 'i', 'g', 0, 'b', 'u', 'i', 'l', 'd', '\n', '"', 0, 0 },
        &source,
    );
}

test "phase 7 string helpers cmdline ownership trims trailing separators while preserving repeated interior boundaries" {
    const source = [_]u8{ 'r', 'u', 'n', 0, 0, 'x', 0, 0 };
    const quoted = (try string_helpers.kstrdup_quotable_cmdline(std.testing.allocator, &source)).?;
    defer std.testing.allocator.free(quoted);

    try std.testing.expectEqualStrings("run  x", quoted);
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'r', 'u', 'n', 0, 0, 'x', 0, 0 },
        &source,
    );
}
