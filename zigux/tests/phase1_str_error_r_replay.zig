const std = @import("std");
const str_error_r = @import("str_error_r");

test "phase1 str_error_r replay keeps known Linux-style messages stable" {
    var success_buffer = [_]u8{0xaa} ** 16;
    const success = str_error_r.strErrorR(0, &success_buffer);
    try std.testing.expectEqualStrings("Success", success);
    try std.testing.expectEqual(@as(u8, 0), success_buffer[success.len]);

    var perm_buffer = [_]u8{0xbb} ** 24;
    const perm = str_error_r.strErrorR(13, &perm_buffer);
    try std.testing.expectEqualStrings("Permission denied", perm);
    try std.testing.expectEqual(@as(u8, 0), perm_buffer[perm.len]);

    var invalid_buffer = [_]u8{0xcc} ** 24;
    const invalid = str_error_r.strErrorR(22, &invalid_buffer);
    try std.testing.expectEqualStrings("Invalid argument", invalid);
    try std.testing.expectEqual(@as(u8, 0), invalid_buffer[invalid.len]);
}

test "phase1 str_error_r replay keeps fallback formatting tied to caller buffer length" {
    var roomy = [_]u8{0xdd} ** 64;
    const roomy_message = str_error_r.strErrorR(4096, &roomy);
    try std.testing.expectEqualStrings(
        "INTERNAL ERROR: strerror_r(4096, [buf], 64)=22",
        roomy_message,
    );
    try std.testing.expectEqual(@as(u8, 0), roomy[roomy_message.len]);

    var medium = [_]u8{0xee} ** 32;
    const medium_message = str_error_r.strErrorR(17, &medium);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(17, ", medium_message);
    try std.testing.expectEqual(@as(u8, 0), medium[medium_message.len]);
}

test "phase1 str_error_r replay truncates tiny buffers and accepts zero-length views" {
    var tiny = [_]u8{0xff} ** 8;
    const tiny_message = str_error_r.strErrorR(4096, &tiny);
    try std.testing.expectEqualStrings("INTERNA", tiny_message);
    try std.testing.expectEqual(@as(u8, 0), tiny[7]);

    var single = [_]u8{0xab};
    const single_message = str_error_r.strErrorR(2, &single);
    try std.testing.expectEqual(@as(usize, 0), single_message.len);
    try std.testing.expectEqual(@as(u8, 0), single[0]);

    var empty_backing = [_]u8{0xcd};
    const empty_message = str_error_r.strErrorR(12, empty_backing[0..0]);
    try std.testing.expectEqual(@as(usize, 0), empty_message.len);
    try std.testing.expectEqual(@as(u8, 0xcd), empty_backing[0]);
}
