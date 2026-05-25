const std = @import("std");
const str_error_r = @import("str_error_r");

test "phase1 str_error_r replay keeps known-message truncation aligned" {
    var short_success: [5]u8 = undefined;
    const short_message = str_error_r.strErrorR(0, &short_success);
    try std.testing.expectEqualStrings("Succ", short_message);
    try std.testing.expectEqual(@as(u8, 0), short_success[4]);

    var exact_success: [8]u8 = undefined;
    const exact_message = str_error_r.strErrorR(0, &exact_success);
    try std.testing.expectEqualStrings("Success", exact_message);
    try std.testing.expectEqual(@as(u8, 0), exact_success[7]);
}

test "phase1 str_error_r replay keeps zero-length and exact known-message buffers aligned" {
    var empty: [0]u8 = .{};
    try std.testing.expectEqualStrings("", str_error_r.strErrorR(22, &empty));

    var permission: [18]u8 = undefined;
    const permission_message = str_error_r.strErrorR(13, &permission);
    try std.testing.expectEqualStrings("Permission denied", permission_message);
    try std.testing.expectEqual(@as(u8, 0), permission[17]);
}

test "phase1 str_error_r replay keeps unknown-message prefixes aligned" {
    var full_buffer: [80]u8 = undefined;
    const full_message = str_error_r.strErrorR(4096, &full_buffer);
    try std.testing.expect(std.mem.startsWith(u8, full_message, "INTERNAL ERROR: strerror_r(4096, [buf], 80)=22"));

    var short_buffer: [12]u8 = undefined;
    const short_message = str_error_r.strErrorR(4096, &short_buffer);
    try std.testing.expectEqualStrings(full_message[0..11], short_message);
    try std.testing.expectEqual(@as(u8, 0), short_buffer[11]);
}
