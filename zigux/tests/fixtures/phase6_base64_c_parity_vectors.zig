const std = @import("std");
const shared = @import("phase6_base64_vectors.zig");

pub const CParityEncodeCase = shared.CParityEncodeCase;
pub const CParityDecodeCase = shared.CParityDecodeCase;
pub const CParityInvalidCase = shared.CParityInvalidCase;

pub const encode_cases = [_]CParityEncodeCase{
    .{ .variant_name = "std", .padding = shared.standard_cases[0].padding, .input = shared.standard_cases[0].input },
    .{ .variant_name = "std", .padding = shared.standard_cases[1].padding, .input = shared.standard_cases[1].input },
    .{ .variant_name = "std", .padding = shared.standard_cases[2].padding, .input = shared.standard_cases[2].input },
    .{ .variant_name = "std", .padding = shared.standard_cases[17].padding, .input = shared.standard_cases[17].input },
    .{ .variant_name = "std", .padding = shared.standard_cases[7].padding, .input = shared.standard_cases[7].input },
    .{ .variant_name = shared.variant_cases[2].variant_name, .padding = shared.variant_cases[2].padding, .input = shared.variant_cases[2].input },
    .{ .variant_name = shared.variant_cases[3].variant_name, .padding = shared.variant_cases[3].padding, .input = shared.variant_cases[3].input },
    .{ .variant_name = shared.variant_cases[8].variant_name, .padding = shared.variant_cases[8].padding, .input = shared.variant_cases[8].input },
    .{ .variant_name = shared.variant_cases[9].variant_name, .padding = shared.variant_cases[9].padding, .input = shared.variant_cases[9].input },
    .{ .variant_name = shared.variant_cases[14].variant_name, .padding = shared.variant_cases[14].padding, .input = shared.variant_cases[14].input },
    .{ .variant_name = shared.variant_cases[15].variant_name, .padding = shared.variant_cases[15].padding, .input = shared.variant_cases[15].input },
    .{ .variant_name = shared.variant_cases[4].variant_name, .padding = shared.variant_cases[4].padding, .input = shared.variant_cases[4].input },
    .{ .variant_name = shared.variant_cases[5].variant_name, .padding = shared.variant_cases[5].padding, .input = shared.variant_cases[5].input },
    .{ .variant_name = shared.variant_cases[10].variant_name, .padding = shared.variant_cases[10].padding, .input = shared.variant_cases[10].input },
    .{ .variant_name = shared.variant_cases[11].variant_name, .padding = shared.variant_cases[11].padding, .input = shared.variant_cases[11].input },
    .{ .variant_name = shared.variant_cases[16].variant_name, .padding = shared.variant_cases[16].padding, .input = shared.variant_cases[16].input },
    .{ .variant_name = shared.variant_cases[17].variant_name, .padding = shared.variant_cases[17].padding, .input = shared.variant_cases[17].input },
};

pub const decode_cases = [_]CParityDecodeCase{
    .{ .variant_name = shared.standard_decode_cases[0].variant_name, .padding = shared.standard_decode_cases[0].padding, .input = shared.standard_decode_cases[0].input },
    .{ .variant_name = shared.standard_decode_cases[1].variant_name, .padding = shared.standard_decode_cases[1].padding, .input = shared.standard_decode_cases[1].input },
    .{ .variant_name = shared.standard_decode_cases[2].variant_name, .padding = shared.standard_decode_cases[2].padding, .input = shared.standard_decode_cases[2].input },
    .{ .variant_name = shared.standard_decode_cases[16].variant_name, .padding = shared.standard_decode_cases[16].padding, .input = shared.standard_decode_cases[16].input },
    .{ .variant_name = shared.standard_decode_cases[7].variant_name, .padding = shared.standard_decode_cases[7].padding, .input = shared.standard_decode_cases[7].input },
    .{ .variant_name = shared.variant_decode_cases[2].variant_name, .padding = shared.variant_decode_cases[2].padding, .input = shared.variant_decode_cases[2].input },
    .{ .variant_name = shared.variant_decode_cases[3].variant_name, .padding = shared.variant_decode_cases[3].padding, .input = shared.variant_decode_cases[3].input },
    .{ .variant_name = shared.variant_decode_cases[8].variant_name, .padding = shared.variant_decode_cases[8].padding, .input = shared.variant_decode_cases[8].input },
    .{ .variant_name = shared.variant_decode_cases[9].variant_name, .padding = shared.variant_decode_cases[9].padding, .input = shared.variant_decode_cases[9].input },
    .{ .variant_name = shared.variant_decode_cases[14].variant_name, .padding = shared.variant_decode_cases[14].padding, .input = shared.variant_decode_cases[14].input },
    .{ .variant_name = shared.variant_decode_cases[15].variant_name, .padding = shared.variant_decode_cases[15].padding, .input = shared.variant_decode_cases[15].input },
    .{ .variant_name = shared.variant_decode_cases[4].variant_name, .padding = shared.variant_decode_cases[4].padding, .input = shared.variant_decode_cases[4].input },
    .{ .variant_name = shared.variant_decode_cases[5].variant_name, .padding = shared.variant_decode_cases[5].padding, .input = shared.variant_decode_cases[5].input },
    .{ .variant_name = shared.variant_decode_cases[10].variant_name, .padding = shared.variant_decode_cases[10].padding, .input = shared.variant_decode_cases[10].input },
    .{ .variant_name = shared.variant_decode_cases[11].variant_name, .padding = shared.variant_decode_cases[11].padding, .input = shared.variant_decode_cases[11].input },
    .{ .variant_name = shared.variant_decode_cases[16].variant_name, .padding = shared.variant_decode_cases[16].padding, .input = shared.variant_decode_cases[16].input },
    .{ .variant_name = shared.variant_decode_cases[17].variant_name, .padding = shared.variant_decode_cases[17].padding, .input = shared.variant_decode_cases[17].input },
};

pub const invalid_cases = [_]CParityInvalidCase{
    .{ .variant_name = shared.invalid_decode_cases[0].variant_name, .padding = shared.invalid_decode_cases[0].padding, .input = shared.invalid_decode_cases[0].input },
    .{ .variant_name = shared.invalid_decode_cases[2].variant_name, .padding = shared.invalid_decode_cases[2].padding, .input = shared.invalid_decode_cases[2].input },
    .{ .variant_name = shared.invalid_decode_cases[11].variant_name, .padding = shared.invalid_decode_cases[11].padding, .input = shared.invalid_decode_cases[11].input },
    .{ .variant_name = shared.invalid_decode_cases[6].variant_name, .padding = shared.invalid_decode_cases[6].padding, .input = shared.invalid_decode_cases[6].input },
    .{ .variant_name = shared.invalid_decode_cases[14].variant_name, .padding = shared.invalid_decode_cases[14].padding, .input = shared.invalid_decode_cases[14].input },
    .{ .variant_name = shared.invalid_decode_cases[15].variant_name, .padding = shared.invalid_decode_cases[15].padding, .input = shared.invalid_decode_cases[15].input },
};

pub fn validate() !void {
    try std.testing.expectEqual(@as(usize, 17), encode_cases.len);
    try std.testing.expectEqual(@as(usize, 17), decode_cases.len);
    try std.testing.expectEqual(@as(usize, 6), invalid_cases.len);
}

test "phase 6 base64 c parity vectors stay aligned with the bounded fixture packet" {
    try validate();
    try std.testing.expectEqualStrings("std", encode_cases[0].variant_name);
    try std.testing.expect(encode_cases[0].padding);
    try std.testing.expectEqualStrings("", encode_cases[0].input);
    try std.testing.expectEqualStrings("urlsafe", encode_cases[5].variant_name);
    try std.testing.expectEqualStrings("APv_f4A", decode_cases[5].input);
    try std.testing.expectEqualStrings("imap", invalid_cases[5].variant_name);
}
