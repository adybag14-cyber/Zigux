const std = @import("std");
const string = @import("string");

test "phase1 string copy-pad replay keeps one-byte destinations terminated" {
    var tiny = [_]u8{0xaa};
    try std.testing.expectEqual(@as(isize, -7), string.strscpy(&tiny, "xy"));
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &tiny);

    var padded_tiny = [_]u8{0xaa};
    try std.testing.expectEqual(@as(isize, -7), string.strscpyPad(&padded_tiny, "xy"));
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &padded_tiny);

    var alias_tiny = [_]u8{0xaa};
    try std.testing.expectEqual(@as(isize, -7), string.strscpy_pad(&alias_tiny, "xy"));
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &alias_tiny);
}

test "phase1 string copy-pad replay separates raw-byte copy from c-string padding" {
    const src_cstr = [_]u8{ 'o', 'k', 0, 'x', 'y' };

    var raw_padded = [_]u8{0xaa} ** 6;
    string.memcpyAndPad(&raw_padded, &src_cstr, 5, '.');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, 'x', 'y', '.' }, &raw_padded);

    var raw_padded_alias = [_]u8{0xaa} ** 5;
    string.memcpy_and_pad(&raw_padded_alias, &src_cstr, 3, '_');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0, '_', '_' }, &raw_padded_alias);

    var cstr_only = [_]u8{0xaa} ** 5;
    string.strtomem(&cstr_only, &src_cstr);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', 0xaa, 0xaa, 0xaa }, &cstr_only);

    var cstr_padded = [_]u8{0xaa} ** 5;
    string.strtomem_pad(&cstr_padded, &src_cstr, '.');
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'o', 'k', '.', '.', '.' }, &cstr_padded);
}

test "phase1 string copy-pad replay keeps memtostr tails zeroed and bounded" {
    const src = [_]u8{ 'z', 'i', 0, 'g' };

    var copied = [_]u8{0xaa} ** 5;
    string.memtostr(&copied, &src);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 0, 0xaa, 0xaa }, &copied);

    var padded = [_]u8{0xaa} ** 5;
    string.memtostrPad(&padded, &src);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 0, 0, 0 }, &padded);

    var alias_padded = [_]u8{0xaa} ** 5;
    string.memtostr_pad(&alias_padded, &src);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'z', 'i', 0, 0, 0 }, &alias_padded);

    var tiny = [_]u8{0xaa};
    string.memtostr(&tiny, &src);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &tiny);

    var tiny_padded = [_]u8{0xaa};
    string.memtostrPad(&tiny_padded, &src);
    try std.testing.expectEqualSlices(u8, &[_]u8{0}, &tiny_padded);
}
