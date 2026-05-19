const std = @import("std");
const ctype = @import("ctype");
const hweight = @import("hweight");

test "phase1 ctype and hweight replay imports the live helper modules" {
    try std.testing.expect(@hasDecl(ctype, "fastTolower"));
    try std.testing.expect(@hasDecl(ctype, "isxdigit"));
    try std.testing.expect(@hasDecl(hweight, "swHweight64"));
    try std.testing.expect(@hasDecl(hweight, "hweight_long"));
}

test "phase1 ctype replay keeps ascii classes and transforms aligned" {
    try std.testing.expect(ctype.isalpha('Q'));
    try std.testing.expect(ctype.isdigit('7'));
    try std.testing.expect(ctype.isspace('\t'));
    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(ctype.isodigit('7'));
    try std.testing.expect(!ctype.isodigit('8'));
    try std.testing.expectEqual(@as(u8, 'm'), ctype.fastTolower('M'));
    try std.testing.expectEqual(@as(u8, 'z'), ctype.tolower('Z'));
    try std.testing.expectEqual(@as(u8, 'A'), ctype.toupper('a'));
    try std.testing.expectEqual(@as(u8, 0x3f), ctype.toascii(0xbf));
    try std.testing.expect(ctype.isupper(0xC0));
    try std.testing.expect(ctype.islower(0xE0));
    try std.testing.expectEqual(@as(u8, 0xF8), ctype.fastTolower(0xD8));
}

test "phase1 hweight replay keeps width-specific helpers and aliases aligned" {
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(0b1111_0000));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(0b1111_0000_1111_0000));
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(0xf0f0_f0f0));
    try std.testing.expectEqual(@as(u64, 32), hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0));
    try std.testing.expectEqual(@popCount(@as(usize, 0xf0f0)), hweight.hweightLong(0xf0f0));
    try std.testing.expectEqual(hweight.swHweight8(0xf0), hweight.__sw_hweight8(0xf0));
    try std.testing.expectEqual(hweight.swHweight16(0xf0f0), hweight.__sw_hweight16(0xf0f0));
    try std.testing.expectEqual(hweight.swHweight32(0xf0f0_f0f0), hweight.__sw_hweight32(0xf0f0_f0f0));
    try std.testing.expectEqual(
        hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0),
        hweight.__sw_hweight64(0xf0f0_f0f0_f0f0_f0f0),
    );
    try std.testing.expectEqual(hweight.hweightLong(0xf0f0), hweight.hweight_long(0xf0f0));
}

test "phase1 ctype and hweight replay cross-checks table-driven bits" {
    const sample = [_]u8{ '0', '9', 'A', 'F', 'a', 'f', ' ', '\n', 0xC0, 0xE0 };
    var mask_bits: u64 = 0;
    for (sample, 0..) |byte, idx| {
        if (ctype.isxdigit(byte)) {
            mask_bits |= (@as(u64, 1) << @intCast(idx));
        }
    }

    try std.testing.expectEqual(@as(u64, 6), hweight.swHweight64(mask_bits));
    try std.testing.expectEqual(@as(usize, 6), hweight.hweightLong(@intCast(mask_bits)));
    try std.testing.expectEqual(@as(u8, ctype._U | ctype._X), ctype.mask('A'));
    try std.testing.expectEqual(@as(u8, ctype._L | ctype._X), ctype.mask('f'));
    try std.testing.expectEqual(@as(u8, ctype._S | ctype._SP), ctype.mask(' '));
}
