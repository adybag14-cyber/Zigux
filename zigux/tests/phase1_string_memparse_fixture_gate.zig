const std = @import("std");
const cmdline = @import("../../tools/lib/cmdline.zig");
const string = @import("../../tools/lib/string.zig");

const CmdlineValueFixture = struct {
    value: u64,
    rest: []const u8,
};

const Fixture = struct {
    cmdline: struct {
        decimal_k: CmdlineValueFixture,
        hex_m: CmdlineValueFixture,
        octal_k: CmdlineValueFixture,
        invalid: CmdlineValueFixture,
        kib: CmdlineValueFixture,
        mb: CmdlineValueFixture,
        gib: CmdlineValueFixture,
        lowercase_kib: CmdlineValueFixture,
    },
};

fn loadFixture(allocator: std.mem.Allocator) !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, allocator, @embedFile("fixtures/phase1_helpers.json"), .{
        .ignore_unknown_fields = true,
    });
}

fn expectMemparseFixture(actual: cmdline.MemparseResult, expected: CmdlineValueFixture) !void {
    try std.testing.expectEqual(expected.value, actual.value);
    try std.testing.expectEqualStrings(expected.rest, actual.rest);
}

test "phase 1 fixture-backed string memparse gate stays aligned with cmdline" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

    try expectMemparseFixture(cmdline.memparse("64K rest"), fixture.cmdline.decimal_k);
    try expectMemparseFixture(cmdline.memparse("0x20M"), fixture.cmdline.hex_m);
    try expectMemparseFixture(cmdline.memparse("010K"), fixture.cmdline.octal_k);
    try expectMemparseFixture(cmdline.memparse("xyz"), fixture.cmdline.invalid);
    try expectMemparseFixture(cmdline.memparse("64KiB rest"), fixture.cmdline.kib);
    try expectMemparseFixture(cmdline.memparse("2MB!"), fixture.cmdline.mb);
    try expectMemparseFixture(cmdline.memparse("1GiB trailing"), fixture.cmdline.gib);
    try expectMemparseFixture(cmdline.memparse("3kib."), fixture.cmdline.lowercase_kib);

    try expectMemparseFixture(string.memparse("64K rest"), fixture.cmdline.decimal_k);
    try expectMemparseFixture(string.memparse("0x20M"), fixture.cmdline.hex_m);
    try expectMemparseFixture(string.memparse("010K"), fixture.cmdline.octal_k);
    try expectMemparseFixture(string.memparse("xyz"), fixture.cmdline.invalid);
    try expectMemparseFixture(string.memparse("64KiB rest"), fixture.cmdline.kib);
    try expectMemparseFixture(string.memparse("2MB!"), fixture.cmdline.mb);
    try expectMemparseFixture(string.memparse("1GiB trailing"), fixture.cmdline.gib);
    try expectMemparseFixture(string.memparse("3kib."), fixture.cmdline.lowercase_kib);
}
