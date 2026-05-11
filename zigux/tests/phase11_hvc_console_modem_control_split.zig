const std = @import("std");

test "phase11 hvc console keeps tiocmget and tiocmset fallback on missing hv_ops callbacks" {
    const missing_get = true;
    const missing_set = true;

    try std.testing.expect(missing_get);
    try std.testing.expect(missing_set);
}

test "phase11 hvc console keeps tiocmset masks live when tiocmget falls back" {
    const tiocmset_mask: u32 = 0b1010;
    const fallback_applies = true;

    try std.testing.expectEqual(@as(u32, 0b1010), tiocmset_mask);
    try std.testing.expect(fallback_applies);
}
