const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

fn expectEncode(input: []const u8, expected: []const u8, padding: bool, variant: base64.Variant) !void {
    var buf: [128]u8 = undefined;
    const written = try base64.encode(buf[0..], input, padding, variant);

    try std.testing.expectEqual(expected.len, written);
    try std.testing.expectEqual(expected.len, base64.chars(input.len, padding));
    try std.testing.expectEqualStrings(expected, buf[0..written]);
}

fn expectExactEncodeBuffer(input: []const u8, expected: []const u8, padding: bool, variant: base64.Variant) !void {
    var exact_buf: [128]u8 = undefined;
    const exact_len = base64.chars(input.len, padding);
    const written = try base64.encode(exact_buf[0..exact_len], input, padding, variant);

    try std.testing.expectEqual(expected.len, exact_len);
    try std.testing.expectEqual(expected.len, written);
    try std.testing.expectEqualStrings(expected, exact_buf[0..written]);

    if (exact_len > 0) {
        try std.testing.expectError(
            base64.EncodeError.DestinationTooSmall,
            base64.encode(exact_buf[0 .. exact_len - 1], input, padding, variant),
        );
    }
}

fn expectFixtureDecode(case: fixtures.DecodeCase) !void {
    var buf: [128]u8 = undefined;
    const variant = fixtureVariant(case.variant_name);
    const exact_len = try base64.bytes(case.input, case.padding, variant);
    const written = try base64.decode(buf[0..], case.input, case.padding, variant);

    try std.testing.expectEqual(case.expected.len, exact_len);
    try std.testing.expectEqual(case.expected.len, written);
    try std.testing.expectEqualSlices(u8, case.expected, buf[0..written]);
}

fn expectExactDecodeBuffer(case: fixtures.DecodeCase) !void {
    var exact_buf: [128]u8 = undefined;
    const variant = fixtureVariant(case.variant_name);
    const exact_len = try base64.bytes(case.input, case.padding, variant);
    const written = try base64.decode(exact_buf[0..exact_len], case.input, case.padding, variant);

    try std.testing.expectEqual(case.expected.len, exact_len);
    try std.testing.expectEqual(case.expected.len, written);
    try std.testing.expectEqualSlices(u8, case.expected, exact_buf[0..written]);

    if (exact_len > 0) {
        try std.testing.expectError(
            base64.DecodeError.DestinationTooSmall,
            base64.decode(exact_buf[0 .. exact_len - 1], case.input, case.padding, variant),
        );
    }
}

fn bytesVariantPinned(input: []const u8, padding: bool, variant: base64.Variant) !usize {
    return switch (variant) {
        .std => base64.bytesStd(input, padding),
        .urlsafe => base64.bytesUrlsafe(input, padding),
        .imap => base64.bytesImap(input, padding),
    };
}

fn decodeVariantPinned(dst: []u8, input: []const u8, padding: bool, variant: base64.Variant) !usize {
    return switch (variant) {
        .std => base64.decodeStd(dst, input, padding),
        .urlsafe => base64.decodeUrlsafe(dst, input, padding),
        .imap => base64.decodeImap(dst, input, padding),
    };
}

fn expectConvenienceVariantForeignAlphabetRejection(
    accepted: []const u8,
    expected: []const u8,
    padding: bool,
    variant: base64.Variant,
    rejected: []const []const u8,
) !void {
    var buf: [8]u8 = undefined;
    const exact_len = try bytesVariantPinned(accepted, padding, variant);
    try std.testing.expectEqual(expected.len, exact_len);
    const written = try decodeVariantPinned(buf[0..], accepted, padding, variant);
    try std.testing.expectEqual(expected.len, written);
    try std.testing.expectEqualSlices(u8, expected, buf[0..written]);

    for (rejected) |input| {
        try std.testing.expectError(base64.DecodeError.InvalidInput, bytesVariantPinned(input, padding, variant));
        try std.testing.expectError(base64.DecodeError.InvalidInput, decodeVariantPinned(buf[0..], input, padding, variant));
    }
}

fn fixtureVariant(name: []const u8) base64.Variant {
    if (std.mem.eql(u8, name, "std")) {
        return .std;
    }
    if (std.mem.eql(u8, name, "urlsafe")) {
        return .urlsafe;
    }
    if (std.mem.eql(u8, name, "imap")) {
        return .imap;
    }
    unreachable;
}

test "phase 6 base64 module imports cleanly" {
    _ = base64;
}

test "phase 6 base64 standard encode parity matches kernel vectors" {
    for (fixtures.standard_cases) |case| {
        try expectEncode(case.input, case.expected, case.padding, .std);
    }
}

test "phase 6 base64 variant alphabets match the kernel mappings" {
    for (fixtures.variant_cases) |case| {
        try expectEncode(case.input, case.expected, case.padding, fixtureVariant(case.variant_name));
    }
}

test "phase 6 base64 standard decode parity matches kernel vectors" {
    for (fixtures.standard_decode_cases) |case| {
        try expectFixtureDecode(case);
    }
}

test "phase 6 base64 decode rejects invalid kernel-style vectors" {
    var buf: [128]u8 = undefined;
    for (fixtures.invalid_decode_cases) |case| {
        const variant = fixtureVariant(case.variant_name);
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytes(case.input, case.padding, variant));
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decode(buf[0..], case.input, case.padding, variant));
    }
}

test "phase 6 base64 variant decode parity matches the kernel mappings" {
    for (fixtures.variant_decode_cases) |case| {
        try expectFixtureDecode(case);
    }
}

test "phase 6 base64 convenience wrappers reject foreign variant tails" {
    try expectConvenienceVariantForeignAlphabetRejection(
        "+w",
        &fixtures.variant_one_byte_sample,
        false,
        .std,
        &[_][]const u8{"-w"},
    );
    try expectConvenienceVariantForeignAlphabetRejection(
        "+w==",
        &fixtures.variant_one_byte_sample,
        true,
        .std,
        &[_][]const u8{"-w=="},
    );
    try expectConvenienceVariantForeignAlphabetRejection(
        "//A",
        &fixtures.variant_two_byte_sample,
        false,
        .std,
        &[_][]const u8{ "__A", ",,A" },
    );
    try expectConvenienceVariantForeignAlphabetRejection(
        "//A=",
        &fixtures.variant_two_byte_sample,
        true,
        .std,
        &[_][]const u8{ "__A=", ",,A=" },
    );

    try expectConvenienceVariantForeignAlphabetRejection(
        "-w",
        &fixtures.variant_one_byte_sample,
        false,
        .urlsafe,
        &[_][]const u8{"+w"},
    );
    try expectConvenienceVariantForeignAlphabetRejection(
        "-w==",
        &fixtures.variant_one_byte_sample,
        true,
        .urlsafe,
        &[_][]const u8{"+w=="},
    );
    try expectConvenienceVariantForeignAlphabetRejection(
        "__A",
        &fixtures.variant_two_byte_sample,
        false,
        .urlsafe,
        &[_][]const u8{ "//A", ",,A" },
    );
    try expectConvenienceVariantForeignAlphabetRejection(
        "__A=",
        &fixtures.variant_two_byte_sample,
        true,
        .urlsafe,
        &[_][]const u8{ "//A=", ",,A=" },
    );

    try expectConvenienceVariantForeignAlphabetRejection(
        "+w",
        &fixtures.variant_one_byte_sample,
        false,
        .imap,
        &[_][]const u8{"-w"},
    );
    try expectConvenienceVariantForeignAlphabetRejection(
        "+w==",
        &fixtures.variant_one_byte_sample,
        true,
        .imap,
        &[_][]const u8{"-w=="},
    );
    try expectConvenienceVariantForeignAlphabetRejection(
        ",,A",
        &fixtures.variant_two_byte_sample,
        false,
        .imap,
        &[_][]const u8{ "//A", "__A" },
    );
    try expectConvenienceVariantForeignAlphabetRejection(
        ",,A=",
        &fixtures.variant_two_byte_sample,
        true,
        .imap,
        &[_][]const u8{ "//A=", "__A=" },
    );
}

test "phase 6 base64 exact-fit buffers work across fixture vectors" {
    for (fixtures.standard_cases) |case| {
        try expectExactEncodeBuffer(case.input, case.expected, case.padding, .std);
    }

    for (fixtures.variant_cases) |case| {
        try expectExactEncodeBuffer(case.input, case.expected, case.padding, fixtureVariant(case.variant_name));
    }

    for (fixtures.standard_decode_cases) |case| {
        try expectExactDecodeBuffer(case);
    }

    for (fixtures.variant_decode_cases) |case| {
        try expectExactDecodeBuffer(case);
    }
}

test "phase 6 base64 reports destination bounds before encoding" {
    var buf: [3]u8 = undefined;
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(buf[0..], "f", true, .std));
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(buf[0..], "foo", false, .std));
}

test "phase 6 base64 reports destination bounds before decoding" {
    var buf: [2]u8 = undefined;
    try std.testing.expectError(base64.DecodeError.DestinationTooSmall, base64.decode(buf[0..], "Zm9v", false, .std));
}

fn encodeVariantPinnedSlice(dst: []u8, input: []const u8, padding: bool, variant: base64.Variant) ![]u8 {
    return switch (variant) {
        .std => base64.encodeStdSlice(dst, input, padding),
        .urlsafe => base64.encodeUrlsafeSlice(dst, input, padding),
        .imap => base64.encodeImapSlice(dst, input, padding),
    };
}

fn encodeVariantPinnedAlloc(allocator: std.mem.Allocator, input: []const u8, padding: bool, variant: base64.Variant) ![]u8 {
    return switch (variant) {
        .std => base64.encodeStdAlloc(allocator, input, padding),
        .urlsafe => base64.encodeUrlsafeAlloc(allocator, input, padding),
        .imap => base64.encodeImapAlloc(allocator, input, padding),
    };
}

fn decodeVariantPinnedSlice(dst: []u8, input: []const u8, padding: bool, variant: base64.Variant) ![]u8 {
    return switch (variant) {
        .std => base64.decodeStdSlice(dst, input, padding),
        .urlsafe => base64.decodeUrlsafeSlice(dst, input, padding),
        .imap => base64.decodeImapSlice(dst, input, padding),
    };
}

fn decodeVariantPinnedAlloc(allocator: std.mem.Allocator, input: []const u8, padding: bool, variant: base64.Variant) ![]u8 {
    return switch (variant) {
        .std => base64.decodeStdAlloc(allocator, input, padding),
        .urlsafe => base64.decodeUrlsafeAlloc(allocator, input, padding),
        .imap => base64.decodeImapAlloc(allocator, input, padding),
    };
}

fn expectConvenienceParityCase(input: []const u8, expected: []const u8, padding: bool, variant: base64.Variant) !void {
    var generic_encode_buf: [128]u8 = [_]u8{0xaa} ** 128;
    var pinned_encode_buf: [128]u8 = [_]u8{0xbb} ** 128;
    const generic_slice = try base64.encodeSlice(generic_encode_buf[0..expected.len], input, padding, variant);
    const pinned_slice = try encodeVariantPinnedSlice(pinned_encode_buf[0..expected.len], input, padding, variant);
    try std.testing.expectEqualStrings(expected, generic_slice);
    try std.testing.expectEqualStrings(expected, pinned_slice);
    try std.testing.expectEqual(@as(u8, 0xaa), generic_encode_buf[generic_slice.len]);
    try std.testing.expectEqual(@as(u8, 0xbb), pinned_encode_buf[pinned_slice.len]);

    const generic_alloc = try base64.encodeAlloc(std.testing.allocator, input, padding, variant);
    defer std.testing.allocator.free(generic_alloc);
    const pinned_alloc = try encodeVariantPinnedAlloc(std.testing.allocator, input, padding, variant);
    defer std.testing.allocator.free(pinned_alloc);
    try std.testing.expectEqualStrings(expected, generic_alloc);
    try std.testing.expectEqualStrings(expected, pinned_alloc);

    const generic_len = try base64.bytes(expected, padding, variant);
    const pinned_len = try bytesVariantPinned(expected, padding, variant);
    try std.testing.expectEqual(generic_len, pinned_len);
    try std.testing.expectEqual(input.len, generic_len);

    var generic_decode_buf: [128]u8 = [_]u8{0xcc} ** 128;
    var pinned_decode_buf: [128]u8 = [_]u8{0xdd} ** 128;
    const generic_decode = try base64.decodeSlice(generic_decode_buf[0..generic_len], expected, padding, variant);
    const pinned_decode = try decodeVariantPinnedSlice(pinned_decode_buf[0..pinned_len], expected, padding, variant);
    try std.testing.expectEqualSlices(u8, input, generic_decode);
    try std.testing.expectEqualSlices(u8, input, pinned_decode);
    try std.testing.expectEqual(@as(u8, 0xcc), generic_decode_buf[generic_decode.len]);
    try std.testing.expectEqual(@as(u8, 0xdd), pinned_decode_buf[pinned_decode.len]);

    const generic_decode_alloc = try base64.decodeAlloc(std.testing.allocator, expected, padding, variant);
    defer std.testing.allocator.free(generic_decode_alloc);
    const pinned_decode_alloc = try decodeVariantPinnedAlloc(std.testing.allocator, expected, padding, variant);
    defer std.testing.allocator.free(pinned_decode_alloc);
    try std.testing.expectEqualSlices(u8, input, generic_decode_alloc);
    try std.testing.expectEqualSlices(u8, input, pinned_decode_alloc);
}

test "phase 6 base64 convenience wrappers stay aligned across fixture-backed slice and alloc paths" {
    for (fixtures.standard_cases) |case| {
        try expectConvenienceParityCase(case.input, case.expected, case.padding, .std);
    }

    for (fixtures.variant_cases) |case| {
        try expectConvenienceParityCase(case.input, case.expected, case.padding, fixtureVariant(case.variant_name));
    }
}
