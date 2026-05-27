const std = @import("std");
const base64 = @import("base64");

test "phase 7 base64 companion replays standard padded convenience wrappers" {
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    var encoded: [8]u8 = undefined;
    const encoded_len = try base64.encodeStd(encoded[0..], &sample, true);

    try std.testing.expectEqual(@as(usize, 8), encoded_len);
    try std.testing.expectEqualStrings("APv/f4A=", encoded[0..encoded_len]);
    try std.testing.expectEqual(@as(usize, 5), try base64.bytesStd(encoded[0..encoded_len], true));

    var decoded: [5]u8 = undefined;
    const decoded_len = try base64.decodeStd(decoded[0..], encoded[0..encoded_len], true);
    try std.testing.expectEqual(@as(usize, 5), decoded_len);
    try std.testing.expectEqualSlices(u8, &sample, decoded[0..decoded_len]);
}

test "phase 7 base64 companion replays urlsafe short-tail wrappers without crossing into standard tails" {
    const one_byte = [_]u8{0xfb};
    var encoded: [2]u8 = undefined;
    const encoded_len = try base64.encodeUrlsafe(encoded[0..], &one_byte, false);

    try std.testing.expectEqual(@as(usize, 2), encoded_len);
    try std.testing.expectEqualStrings("-w", encoded[0..encoded_len]);
    try std.testing.expectEqual(@as(usize, 1), try base64.bytesUrlsafe(encoded[0..encoded_len], false));

    var decoded: [1]u8 = undefined;
    const decoded_len = try base64.decodeUrlsafe(decoded[0..], encoded[0..encoded_len], false);
    try std.testing.expectEqual(@as(usize, 1), decoded_len);
    try std.testing.expectEqualSlices(u8, &one_byte, decoded[0..decoded_len]);

    try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytesUrlsafe("+w", false));
    try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decodeUrlsafe(decoded[0..], "+w", false));
}

test "phase 7 base64 companion replays IMAP short-tail wrappers without slash-backed standard tails" {
    const two_bytes = [_]u8{ 0xff, 0xf0 };
    var encoded: [4]u8 = undefined;
    const encoded_len = try base64.encodeImap(encoded[0..], &two_bytes, true);

    try std.testing.expectEqual(@as(usize, 4), encoded_len);
    try std.testing.expectEqualStrings(",,A=", encoded[0..encoded_len]);
    try std.testing.expectEqual(@as(usize, 2), try base64.bytesImap(encoded[0..encoded_len], true));

    var decoded: [2]u8 = undefined;
    const decoded_len = try base64.decodeImap(decoded[0..], encoded[0..encoded_len], true);
    try std.testing.expectEqual(@as(usize, 2), decoded_len);
    try std.testing.expectEqualSlices(u8, &two_bytes, decoded[0..decoded_len]);

    try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytesImap("//A=", true));
    try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decodeImap(decoded[0..], "//A=", true));
}

test "phase 7 base64 companion replays exact-span slice and allocator companions" {
    const sample = [_]u8{ 0x00, 0xfb, 0xff, 0x7f, 0x80 };
    var encoded: [8]u8 = [_]u8{0xaa} ** 8;
    const encoded_slice = try base64.encodeStdSlice(encoded[0..], &sample, true);
    defer {
        for (encoded_slice) |_| {}
    }

    try std.testing.expectEqualStrings("APv/f4A=", encoded_slice);

    const encoded_alloc = try base64.encodeStdAlloc(std.testing.allocator, &sample, true);
    defer std.testing.allocator.free(encoded_alloc);
    try std.testing.expectEqualStrings("APv/f4A=", encoded_alloc);

    var decoded: [5]u8 = [_]u8{0xbb} ** 5;
    const decoded_slice = try base64.decodeStdSlice(decoded[0..], encoded_slice, true);
    try std.testing.expectEqualSlices(u8, &sample, decoded_slice);

    const decoded_alloc = try base64.decodeStdAlloc(std.testing.allocator, encoded_slice, true);
    defer std.testing.allocator.free(decoded_alloc);
    try std.testing.expectEqualSlices(u8, &sample, decoded_alloc);
}
