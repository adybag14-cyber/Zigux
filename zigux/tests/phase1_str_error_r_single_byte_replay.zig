const std = @import("std");
const str_error_r = @import("str_error_r");

test "phase1 str_error_r replay keeps single-byte known-message buffers terminated" {
    var success = [_]u8{0xaa};
    const rendered = str_error_r.strErrorR(0, &success);
    try std.testing.expectEqualStrings("", rendered);
    try std.testing.expectEqual(@as(u8, 0), success[0]);

    var permission = [_]u8{0xbb};
    const permission_rendered = str_error_r.strErrorR(13, &permission);
    try std.testing.expectEqualStrings("", permission_rendered);
    try std.testing.expectEqual(@as(u8, 0), permission[0]);
}

test "phase1 str_error_r replay keeps single-byte fallback buffers terminated" {
    var unknown = [_]u8{0xcc};
    const rendered = str_error_r.strErrorR(4096, &unknown);
    try std.testing.expectEqualStrings("", rendered);
    try std.testing.expectEqual(@as(u8, 0), unknown[0]);

    var negative = [_]u8{0xdd};
    const negative_rendered = str_error_r.strErrorR(-9, &negative);
    try std.testing.expectEqualStrings("", negative_rendered);
    try std.testing.expectEqual(@as(u8, 0), negative[0]);
}

test "phase1 str_error_r replay keeps fallback buffer lengths and negative errnums visible" {
    var full_buffer: [80]u8 = undefined;
    const full_message = str_error_r.strErrorR(-9, &full_buffer);
    try std.testing.expectEqualStrings(
        "INTERNAL ERROR: strerror_r(-9, [buf], 80)=22",
        full_message,
    );

    var shorter_buffer: [16]u8 = undefined;
    const shorter_message = str_error_r.strErrorR(-9, &shorter_buffer);
    try std.testing.expectEqualStrings("INTERNAL ERROR:", shorter_message);
    try std.testing.expectEqual(@as(u8, 0), shorter_buffer[15]);
}
