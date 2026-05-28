const std = @import("std");

fn copyMessage(buffer: []u8, message: []const u8) []const u8 {
    if (buffer.len == 0) {
        return buffer[0..0];
    }

    const count = @min(message.len, buffer.len - 1);
    if (count != 0) {
        @memcpy(buffer[0..count], message[0..count]);
    }
    buffer[count] = 0;
    return buffer[0..count];
}

fn knownMessage(errnum: i32) ?[]const u8 {
    return switch (errnum) {
        0 => "Success",
        2 => "No such file or directory",
        12 => "Cannot allocate memory",
        13 => "Permission denied",
        22 => "Invalid argument",
        else => null,
    };
}

pub fn strErrorR(errnum: i32, buffer: []u8) []const u8 {
    if (knownMessage(errnum)) |message| {
        return copyMessage(buffer, message);
    }

    var scratch: [64]u8 = undefined;
    const rendered = std.fmt.bufPrint(
        &scratch,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ errnum, buffer.len },
    ) catch "INTERNAL ERROR: strerror_r failed";
    return copyMessage(buffer, rendered);
}

test "strErrorR returns deterministic Linux-style messages" {
    var buffer: [64]u8 = undefined;
    try std.testing.expectEqualStrings("No such file or directory", strErrorR(2, &buffer));
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 64)=22", strErrorR(4096, &buffer));
}

test "strErrorR truncates known messages and keeps a terminator" {
    var buffer: [6]u8 = undefined;
    const rendered = strErrorR(0, &buffer);
    try std.testing.expectEqualStrings("Succe", rendered);
    try std.testing.expectEqual(@as(u8, 0), buffer[5]);
}

test "strErrorR truncates generated internal errors and keeps a terminator" {
    var buffer: [12]u8 = undefined;
    const rendered = strErrorR(4096, &buffer);

    var expected_storage: [64]u8 = undefined;
    const full = try std.fmt.bufPrint(
        &expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, buffer.len },
    );

    try std.testing.expectEqualStrings(full[0 .. buffer.len - 1], rendered);
    try std.testing.expectEqual(@as(u8, 0), buffer[buffer.len - 1]);
}

test "strErrorR handles empty and single-byte buffers without exposing bytes" {
    var empty: [0]u8 = undefined;
    try std.testing.expectEqualStrings("", strErrorR(2, &empty));

    var tiny = [_]u8{0xaa};
    const rendered = strErrorR(4096, &tiny);
    try std.testing.expectEqualStrings("", rendered);
    try std.testing.expectEqual(@as(u8, 0), tiny[0]);
}

test "strErrorR returns full messages when buffers fit exactly" {
    var success_buffer: [8]u8 = undefined;
    const success_rendered = strErrorR(0, &success_buffer);
    try std.testing.expectEqualStrings("Success", success_rendered);
    try std.testing.expectEqual(@as(u8, 0), success_buffer[success_rendered.len]);

    var internal_storage: [64]u8 = undefined;
    const expected_internal = try std.fmt.bufPrint(
        &internal_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, 48 },
    );

    var exact_buffer: [48]u8 = undefined;
    const exact_rendered = strErrorR(4096, &exact_buffer);
    try std.testing.expectEqualStrings(expected_internal, exact_rendered);
    try std.testing.expectEqual(@as(u8, 0), exact_buffer[exact_rendered.len]);
}

test "strErrorR returns slices backed by the caller buffer" {
    var known_buffer: [8]u8 = undefined;
    const known_rendered = strErrorR(0, &known_buffer);
    try std.testing.expectEqual(@intFromPtr(&known_buffer[0]), @intFromPtr(known_rendered.ptr));

    var generated_buffer: [48]u8 = undefined;
    const generated_rendered = strErrorR(4096, &generated_buffer);
    try std.testing.expectEqual(@intFromPtr(&generated_buffer[0]), @intFromPtr(generated_rendered.ptr));
}

test "strErrorR reuses caller buffers cleanly after longer messages" {
    var buffer = [_]u8{0xaa} ** 64;
    const long_rendered = strErrorR(4096, &buffer);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 64)=22", long_rendered);

    const success_rendered = strErrorR(0, &buffer);
    try std.testing.expectEqualStrings("Success", success_rendered);
    try std.testing.expectEqual(@as(u8, 0), buffer[success_rendered.len]);

    const permission_rendered = strErrorR(13, &buffer);
    try std.testing.expectEqualStrings("Permission denied", permission_rendered);
    try std.testing.expectEqual(@as(u8, 0), buffer[permission_rendered.len]);
}

test "strErrorR reuses smaller caller slices after a longer render" {
    var storage = [_]u8{0xaa} ** 64;
    const long_rendered = strErrorR(4096, storage[0..]);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 64)=22", long_rendered);

    const single_byte_rendered = strErrorR(0, storage[0..1]);
    try std.testing.expectEqualStrings("", single_byte_rendered);
    try std.testing.expectEqual(@as(u8, 0), storage[0]);

    const truncated_permission = strErrorR(13, storage[0..6]);
    try std.testing.expectEqualStrings("Permi", truncated_permission);
    try std.testing.expectEqual(@as(u8, 0), storage[5]);
}

test "strErrorR reuses larger caller slices after an earlier truncation" {
    var storage = [_]u8{0xaa} ** 64;

    const truncated = strErrorR(13, storage[0..6]);
    try std.testing.expectEqualStrings("Permi", truncated);
    try std.testing.expectEqual(@as(u8, 0), storage[5]);

    const exact_fit = strErrorR(13, storage[0..18]);
    try std.testing.expectEqualStrings("Permission denied", exact_fit);
    try std.testing.expectEqual(@as(u8, 0), storage[exact_fit.len]);
}

test "strErrorR grows generated renders back to exact-fit caller slices" {
    var storage = [_]u8{0xaa} ** 64;

    var small_expected_storage: [64]u8 = undefined;
    const small_expected = try std.fmt.bufPrint(
        &small_expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, 12 },
    );

    const truncated = strErrorR(4096, storage[0..12]);
    try std.testing.expectEqualStrings(small_expected[0 .. 12 - 1], truncated);
    try std.testing.expectEqual(@as(u8, 0), storage[11]);

    var large_expected_storage: [64]u8 = undefined;
    const large_expected = try std.fmt.bufPrint(
        &large_expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, 48 },
    );

    const exact_fit = strErrorR(4096, storage[0..48]);
    try std.testing.expectEqualStrings(large_expected, exact_fit);
    try std.testing.expectEqual(@as(u8, 0), storage[exact_fit.len]);
}

test "strErrorR respects offset caller slices and leaves neighboring bytes untouched" {
    var storage = [_]u8{0xaa} ** 64;

    const known_view = storage[3..11];
    const known_rendered = strErrorR(0, known_view);
    try std.testing.expectEqual(@intFromPtr(&storage[3]), @intFromPtr(known_rendered.ptr));
    try std.testing.expectEqualStrings("Success", known_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[2]);
    try std.testing.expectEqual(@as(u8, 0), storage[10]);
    try std.testing.expectEqual(@as(u8, 0xaa), storage[11]);

    @memset(storage[0..], 0xbb);

    const generated_view = storage[7..19];
    var expected_storage: [64]u8 = undefined;
    const expected = try std.fmt.bufPrint(
        &expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, generated_view.len },
    );
    const generated_rendered = strErrorR(4096, generated_view);
    try std.testing.expectEqual(@intFromPtr(&storage[7]), @intFromPtr(generated_rendered.ptr));
    try std.testing.expectEqualStrings(expected[0 .. generated_view.len - 1], generated_rendered);
    try std.testing.expectEqual(@as(u8, 0xbb), storage[6]);
    try std.testing.expectEqual(@as(u8, 0), storage[18]);
    try std.testing.expectEqual(@as(u8, 0xbb), storage[19]);
}

test "strErrorR reuses offset caller slices after tiny generated renders" {
    var storage = [_]u8{0xcc} ** 64;
    const view = storage[5..23];

    var tiny_expected_storage: [64]u8 = undefined;
    const tiny_expected = try std.fmt.bufPrint(
        &tiny_expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, 12 },
    );

    const tiny_rendered = strErrorR(4096, view[0..12]);
    try std.testing.expectEqual(@intFromPtr(&storage[5]), @intFromPtr(tiny_rendered.ptr));
    try std.testing.expectEqualStrings(tiny_expected[0 .. 12 - 1], tiny_rendered);
    try std.testing.expectEqual(@as(u8, 0xcc), storage[4]);
    try std.testing.expectEqual(@as(u8, 0), storage[16]);
    try std.testing.expectEqual(@as(u8, 0xcc), storage[17]);

    const exact_known = strErrorR(13, view);
    try std.testing.expectEqual(@intFromPtr(&storage[5]), @intFromPtr(exact_known.ptr));
    try std.testing.expectEqualStrings("Permission denied", exact_known);
    try std.testing.expectEqual(@as(u8, 0xcc), storage[4]);
    try std.testing.expectEqual(@as(u8, 0), storage[22]);
    try std.testing.expectEqual(@as(u8, 0xcc), storage[23]);
}

test "strErrorR respects nested offset subslices inside offset caller views" {
    var storage = [_]u8{0xdd} ** 64;
    const view = storage[5..23];

    const exact_known = strErrorR(13, view);
    try std.testing.expectEqual(@intFromPtr(&storage[5]), @intFromPtr(exact_known.ptr));
    try std.testing.expectEqualStrings("Permission denied", exact_known);
    try std.testing.expectEqual(@as(u8, 0xdd), storage[4]);
    try std.testing.expectEqual(@as(u8, 0), storage[22]);
    try std.testing.expectEqual(@as(u8, 0xdd), storage[23]);

    const nested_view = view[4..10];
    var nested_expected_storage: [64]u8 = undefined;
    const nested_expected = try std.fmt.bufPrint(
        &nested_expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, nested_view.len },
    );

    const nested_rendered = strErrorR(4096, nested_view);
    try std.testing.expectEqual(@intFromPtr(&storage[9]), @intFromPtr(nested_rendered.ptr));
    try std.testing.expectEqualStrings(nested_expected[0 .. nested_view.len - 1], nested_rendered);
    try std.testing.expectEqual(@as(u8, 'm'), storage[8]);
    try std.testing.expectEqual(@as(u8, 0), storage[14]);
    try std.testing.expectEqual(@as(u8, ' '), storage[15]);
    try std.testing.expectEqual(@as(u8, 0), storage[22]);
    try std.testing.expectEqualStrings("Perm", view[0..4]);
}
