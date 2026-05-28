const std = @import("std");
const string = @import("string");

const fixture_bytes = @embedFile("fixtures/phase1_string_replay.json");

const Fixture = struct {
    string: struct {
        strlcat_len: usize,
        strlcat_buffer: []const u8,
        strlcat_unterminated_len: usize,
        strlcat_zero_dest_len: usize,
        strlcat_embedded_nul_src_len: usize,
        strlcat_embedded_nul_src_bytes: []const u8,
    },
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

test "phase 1 string replay locks strlcat boundary behavior" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value.string;

    var truncated = [_]u8{ 'a', 'b', 0, 'x' };
    try std.testing.expectEqual(fixture.strlcat_len, string.strlcat(truncated[0..], "cdef"));
    try std.testing.expectEqualStrings(fixture.strlcat_buffer, truncated[0 .. truncated.len - 1]);

    var unterminated = [_]u8{ 'a', 'b', 'c' };
    try std.testing.expectEqual(fixture.strlcat_unterminated_len, string.strlcat(unterminated[0..], "xyz"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c' }, unterminated[0..]);

    var empty = [_]u8{};
    try std.testing.expectEqual(fixture.strlcat_zero_dest_len, string.strlcat(empty[0..], "zig"));

    var embedded = [_]u8{ 'a', 0, 'x', 'x' };
    const src = [_]u8{ 'b', 'c', 0, 'd' };
    try std.testing.expectEqual(fixture.strlcat_embedded_nul_src_len, string.strlcat(embedded[0..], &src));
    try std.testing.expectEqualSlices(u8, fixture.strlcat_embedded_nul_src_bytes, embedded[0..]);
}
