const std = @import("std");
const base64 = @import("base64");
const fixtures = @import("fixtures/phase6_base64_vectors.zig");

const DecodeCase = struct {
    input: []const u8,
    expected: []const u8,
    padding: bool,
    variant: base64.Variant,
};

fn expectEncode(input: []const u8, expected: []const u8, padding: bool, variant: base64.Variant) !void {
    var buf: [128]u8 = undefined;
    const written = try base64.encode(buf[0..], input, padding, variant);

    try std.testing.expectEqual(expected.len, written);
    try std.testing.expectEqual(expected.len, base64.chars(input.len, padding));
    try std.testing.expectEqualStrings(expected, buf[0..written]);
}

fn expectDecode(case: DecodeCase) !void {
    var buf: [128]u8 = undefined;
    const decoded_len = try base64.bytes(case.input, case.padding, case.variant);
    try std.testing.expectEqual(case.expected.len, decoded_len);

    const written = try base64.decode(buf[0..], case.input, case.padding, case.variant);
    try std.testing.expectEqual(case.expected.len, written);
    try std.testing.expectEqualSlices(u8, case.expected, buf[0..written]);
}

fn bytesVariantPinned(input: []const u8, padding: bool, variant: base64.Variant) base64.DecodeError!usize {
    return switch (variant) {
        .std => base64.bytesStd(input, padding),
        .urlsafe => base64.bytesUrlsafe(input, padding),
        .imap => base64.bytesImap(input, padding),
    };
}

fn encodeVariantPinned(dst: []u8, input: []const u8, padding: bool, variant: base64.Variant) base64.EncodeError!usize {
    return switch (variant) {
        .std => base64.encodeStd(dst, input, padding),
        .urlsafe => base64.encodeUrlsafe(dst, input, padding),
        .imap => base64.encodeImap(dst, input, padding),
    };
}

fn encodeVariantPinnedSlice(dst: []u8, input: []const u8, padding: bool, variant: base64.Variant) base64.EncodeError![]u8 {
    return switch (variant) {
        .std => base64.encodeStdSlice(dst, input, padding),
        .urlsafe => base64.encodeUrlsafeSlice(dst, input, padding),
        .imap => base64.encodeImapSlice(dst, input, padding),
    };
}

fn encodeVariantPinnedAlloc(allocator: std.mem.Allocator, input: []const u8, padding: bool, variant: base64.Variant) base64.EncodeAllocError![]u8 {
    return switch (variant) {
        .std => base64.encodeStdAlloc(allocator, input, padding),
        .urlsafe => base64.encodeUrlsafeAlloc(allocator, input, padding),
        .imap => base64.encodeImapAlloc(allocator, input, padding),
    };
}

fn decodeVariantPinned(dst: []u8, input: []const u8, padding: bool, variant: base64.Variant) base64.DecodeError!usize {
    return switch (variant) {
        .std => base64.decodeStd(dst, input, padding),
        .urlsafe => base64.decodeUrlsafe(dst, input, padding),
        .imap => base64.decodeImap(dst, input, padding),
    };
}

fn decodeVariantPinnedSlice(dst: []u8, input: []const u8, padding: bool, variant: base64.Variant) base64.DecodeError![]u8 {
    return switch (variant) {
        .std => base64.decodeStdSlice(dst, input, padding),
        .urlsafe => base64.decodeUrlsafeSlice(dst, input, padding),
        .imap => base64.decodeImapSlice(dst, input, padding),
    };
}

fn decodeVariantPinnedAlloc(allocator: std.mem.Allocator, input: []const u8, padding: bool, variant: base64.Variant) base64.DecodeAllocError![]u8 {
    return switch (variant) {
        .std => base64.decodeStdAlloc(allocator, input, padding),
        .urlsafe => base64.decodeUrlsafeAlloc(allocator, input, padding),
        .imap => base64.decodeImapAlloc(allocator, input, padding),
    };
}

fn expectConvenienceVariantForeignAlphabetRejection(padding: bool) !void {
    const payload = [_]u8{ 0xfb, 0xff };
    const untouched = [_]u8{0xa5} ** 8;
    const cases = [_]struct {
        variant: base64.Variant,
        encoded: []const u8,
    }{
        .{ .variant = .std, .encoded = if (padding) "+/8=" else "+/8" },
        .{ .variant = .urlsafe, .encoded = if (padding) "-_8=" else "-_8" },
        .{ .variant = .imap, .encoded = if (padding) "+,8=" else "+,8" },
    };

    for (cases) |owner| {
        try std.testing.expectEqual(payload.len, try bytesVariantPinned(owner.encoded, padding, owner.variant));

        var accepted_buf = untouched;
        const accepted_len = try decodeVariantPinned(accepted_buf[0..], owner.encoded, padding, owner.variant);
        try std.testing.expectEqual(payload.len, accepted_len);
        try std.testing.expectEqualSlices(u8, payload[0..], accepted_buf[0..accepted_len]);
        try std.testing.expectEqual(@as(u8, untouched[payload.len]), accepted_buf[payload.len]);

        for (cases) |foreign| {
            if (foreign.variant == owner.variant) {
                continue;
            }

            try std.testing.expectError(base64.DecodeError.InvalidInput, bytesVariantPinned(foreign.encoded, padding, owner.variant));

            var rejected_buf = untouched;
            try std.testing.expectError(base64.DecodeError.InvalidInput, decodeVariantPinned(rejected_buf[0..], foreign.encoded, padding, owner.variant));
            try std.testing.expectEqualSlices(u8, untouched[0..], rejected_buf[0..]);
        }
    }
}

fn expectConvenienceWrapperRoundTrip(input: []const u8, expected: []const u8, padding: bool, variant: base64.Variant) !void {
    var direct_encoded_buf = [_]u8{0xaa} ** 128;
    var slice_encoded_buf = [_]u8{0xbb} ** 128;
    var direct_decoded_buf = [_]u8{0xcc} ** 128;
    var slice_decoded_buf = [_]u8{0xdd} ** 128;

    const direct_encoded_len = try encodeVariantPinned(direct_encoded_buf[0..], input, padding, variant);
    try std.testing.expectEqual(expected.len, direct_encoded_len);
    try std.testing.expectEqual(expected.len, base64.chars(input.len, padding));
    try std.testing.expectEqualStrings(expected, direct_encoded_buf[0..direct_encoded_len]);
    try std.testing.expectEqual(@as(u8, 0xaa), direct_encoded_buf[direct_encoded_len]);

    const slice_encoded = try encodeVariantPinnedSlice(slice_encoded_buf[0..], input, padding, variant);
    try std.testing.expectEqualStrings(expected, slice_encoded);
    try std.testing.expectEqual(@as(u8, 0xbb), slice_encoded_buf[slice_encoded.len]);

    const alloc_encoded = try encodeVariantPinnedAlloc(std.testing.allocator, input, padding, variant);
    defer std.testing.allocator.free(alloc_encoded);
    try std.testing.expectEqualStrings(expected, alloc_encoded);

    try std.testing.expectEqual(input.len, try bytesVariantPinned(expected, padding, variant));

    const direct_decoded_len = try decodeVariantPinned(direct_decoded_buf[0..], expected, padding, variant);
    try std.testing.expectEqual(input.len, direct_decoded_len);
    try std.testing.expectEqualSlices(u8, input, direct_decoded_buf[0..direct_decoded_len]);
    try std.testing.expectEqual(@as(u8, 0xcc), direct_decoded_buf[direct_decoded_len]);

    const slice_decoded = try decodeVariantPinnedSlice(slice_decoded_buf[0..], expected, padding, variant);
    try std.testing.expectEqualSlices(u8, input, slice_decoded);
    try std.testing.expectEqual(@as(u8, 0xdd), slice_decoded_buf[slice_decoded.len]);

    const alloc_decoded = try decodeVariantPinnedAlloc(std.testing.allocator, expected, padding, variant);
    defer std.testing.allocator.free(alloc_decoded);
    try std.testing.expectEqualSlices(u8, input, alloc_decoded);
}

fn expectConvenienceWrapperAliasParity(input: []const u8, padding: bool, variant: base64.Variant) !void {
    var generic_direct_encoded_buf = [_]u8{0x91} ** 128;
    var pinned_direct_encoded_buf = [_]u8{0xa2} ** 128;
    var generic_slice_encoded_buf = [_]u8{0xb3} ** 128;
    var pinned_slice_encoded_buf = [_]u8{0xc4} ** 128;
    var generic_direct_decoded_buf = [_]u8{0xd5} ** 128;
    var pinned_direct_decoded_buf = [_]u8{0xe6} ** 128;
    var generic_slice_decoded_buf = [_]u8{0xf7} ** 128;
    var pinned_slice_decoded_buf = [_]u8{0x18} ** 128;

    const generic_direct_encoded_len = try base64.encode(generic_direct_encoded_buf[0..], input, padding, variant);
    const pinned_direct_encoded_len = try encodeVariantPinned(pinned_direct_encoded_buf[0..], input, padding, variant);
    try std.testing.expectEqual(generic_direct_encoded_len, pinned_direct_encoded_len);
    try std.testing.expectEqualSlices(u8, generic_direct_encoded_buf[0..generic_direct_encoded_len], pinned_direct_encoded_buf[0..pinned_direct_encoded_len]);
    try std.testing.expectEqual(@as(u8, 0x91), generic_direct_encoded_buf[generic_direct_encoded_len]);
    try std.testing.expectEqual(@as(u8, 0xa2), pinned_direct_encoded_buf[pinned_direct_encoded_len]);

    const generic_slice_encoded = try base64.encodeSlice(generic_slice_encoded_buf[0..], input, padding, variant);
    const pinned_slice_encoded = try encodeVariantPinnedSlice(pinned_slice_encoded_buf[0..], input, padding, variant);
    try std.testing.expectEqualSlices(u8, generic_direct_encoded_buf[0..generic_direct_encoded_len], generic_slice_encoded);
    try std.testing.expectEqualSlices(u8, generic_direct_encoded_buf[0..generic_direct_encoded_len], pinned_slice_encoded);
    try std.testing.expectEqual(@as(u8, 0xb3), generic_slice_encoded_buf[generic_slice_encoded.len]);
    try std.testing.expectEqual(@as(u8, 0xc4), pinned_slice_encoded_buf[pinned_slice_encoded.len]);

    const generic_alloc_encoded = try base64.encodeAlloc(std.testing.allocator, input, padding, variant);
    defer std.testing.allocator.free(generic_alloc_encoded);
    const pinned_alloc_encoded = try encodeVariantPinnedAlloc(std.testing.allocator, input, padding, variant);
    defer std.testing.allocator.free(pinned_alloc_encoded);
    try std.testing.expectEqualSlices(u8, generic_direct_encoded_buf[0..generic_direct_encoded_len], generic_alloc_encoded);
    try std.testing.expectEqualSlices(u8, generic_direct_encoded_buf[0..generic_direct_encoded_len], pinned_alloc_encoded);

    const encoded = generic_direct_encoded_buf[0..generic_direct_encoded_len];
    try std.testing.expectEqual(try base64.bytes(encoded, padding, variant), try bytesVariantPinned(encoded, padding, variant));

    const generic_direct_decoded_len = try base64.decode(generic_direct_decoded_buf[0..], encoded, padding, variant);
    const pinned_direct_decoded_len = try decodeVariantPinned(pinned_direct_decoded_buf[0..], encoded, padding, variant);
    try std.testing.expectEqual(generic_direct_decoded_len, pinned_direct_decoded_len);
    try std.testing.expectEqualSlices(u8, generic_direct_decoded_buf[0..generic_direct_decoded_len], pinned_direct_decoded_buf[0..pinned_direct_decoded_len]);
    try std.testing.expectEqual(@as(u8, 0xd5), generic_direct_decoded_buf[generic_direct_decoded_len]);
    try std.testing.expectEqual(@as(u8, 0xe6), pinned_direct_decoded_buf[pinned_direct_decoded_len]);

    const generic_slice_decoded = try base64.decodeSlice(generic_slice_decoded_buf[0..], encoded, padding, variant);
    const pinned_slice_decoded = try decodeVariantPinnedSlice(pinned_slice_decoded_buf[0..], encoded, padding, variant);
    try std.testing.expectEqualSlices(u8, generic_direct_decoded_buf[0..generic_direct_decoded_len], generic_slice_decoded);
    try std.testing.expectEqualSlices(u8, generic_direct_decoded_buf[0..generic_direct_decoded_len], pinned_slice_decoded);
    try std.testing.expectEqual(@as(u8, 0xf7), generic_slice_decoded_buf[generic_slice_decoded.len]);
    try std.testing.expectEqual(@as(u8, 0x18), pinned_slice_decoded_buf[pinned_slice_decoded.len]);

    const generic_alloc_decoded = try base64.decodeAlloc(std.testing.allocator, encoded, padding, variant);
    defer std.testing.allocator.free(generic_alloc_decoded);
    const pinned_alloc_decoded = try decodeVariantPinnedAlloc(std.testing.allocator, encoded, padding, variant);
    defer std.testing.allocator.free(pinned_alloc_decoded);
    try std.testing.expectEqualSlices(u8, generic_direct_decoded_buf[0..generic_direct_decoded_len], generic_alloc_decoded);
    try std.testing.expectEqualSlices(u8, generic_direct_decoded_buf[0..generic_direct_decoded_len], pinned_alloc_decoded);
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

test "phase 6 base64 chars reports exact padded and unpadded lengths" {
    const cases = [_]struct {
        len: usize,
        padding: bool,
        expected: usize,
    }{
        .{ .len = 0, .padding = true, .expected = 0 },
        .{ .len = 1, .padding = true, .expected = 4 },
        .{ .len = 2, .padding = true, .expected = 4 },
        .{ .len = 3, .padding = true, .expected = 4 },
        .{ .len = 4, .padding = true, .expected = 8 },
        .{ .len = 0, .padding = false, .expected = 0 },
        .{ .len = 1, .padding = false, .expected = 2 },
        .{ .len = 2, .padding = false, .expected = 3 },
        .{ .len = 3, .padding = false, .expected = 4 },
        .{ .len = 4, .padding = false, .expected = 6 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected, base64.chars(case.len, case.padding));
    }
}

test "phase 6 base64 bytes reports exact decoded lengths for kernel-aligned vectors" {
    const cases = [_]struct {
        input: []const u8,
        padding: bool,
        variant: base64.Variant,
        expected: usize,
    }{
        .{ .input = "TQ==", .padding = true, .variant = .std, .expected = 1 },
        .{ .input = "TWE=", .padding = true, .variant = .std, .expected = 2 },
        .{ .input = "TWFu", .padding = false, .variant = .std, .expected = 3 },
        .{ .input = "APv_f4A", .padding = false, .variant = .urlsafe, .expected = 5 },
        .{ .input = "APv,f4A=", .padding = true, .variant = .imap, .expected = 5 },
    };

    for (cases) |case| {
        try std.testing.expectEqual(case.expected, try base64.bytes(case.input, case.padding, case.variant));
    }
}

test "phase 6 base64 standard encode parity matches kernel vectors" {
    for (fixtures.standard_cases) |case| {
        try expectEncode(case.input, case.expected, case.padding, .std);
    }
}

test "phase 6 base64 variant alphabets match the kernel mappings with and without padding" {
    for (fixtures.variant_cases) |case| {
        try expectEncode(&fixtures.variant_sample, case.expected, case.padding, fixtureVariant(case.variant_name));
    }
}

test "phase 6 base64 standard decode parity keeps bytes and decode aligned with kernel vectors" {
    for (fixtures.standard_decode_cases) |case| {
        try expectDecode(.{
            .input = case.input,
            .expected = case.expected,
            .padding = case.padding,
            .variant = fixtureVariant(case.variant_name),
        });
    }
}

test "phase 6 base64 invalid vectors fail bytes and decode together" {
    var buf: [128]u8 = undefined;
    for (fixtures.invalid_decode_cases) |case| {
        const variant = fixtureVariant(case.variant_name);
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytes(case.input, case.padding, variant));
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decode(buf[0..], case.input, case.padding, variant));
    }
}

test "phase 6 base64 invalid decode vectors leave destination bytes untouched" {
    for (fixtures.invalid_decode_cases) |case| {
        const variant = fixtureVariant(case.variant_name);
        var buf = [_]u8{0xee} ** 32;

        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.decode(buf[0..], case.input, case.padding, variant));
        try std.testing.expectEqualSlices(u8, &([_]u8{0xee} ** 32), buf[0..]);
    }
}

test "phase 6 base64 bytes rejects malformed kernel-style vectors" {
    const cases = [_]struct {
        input: []const u8,
        padding: bool,
        variant: base64.Variant,
    }{
        .{ .input = "A", .padding = false, .variant = .std },
        .{ .input = "Zh==", .padding = true, .variant = .std },
        .{ .input = "Zm9=", .padding = false, .variant = .std },
        .{ .input = "Zg==", .padding = false, .variant = .urlsafe },
    };

    for (cases) |case| {
        try std.testing.expectError(base64.DecodeError.InvalidInput, base64.bytes(case.input, case.padding, case.variant));
    }
}

test "phase 6 base64 variant decode parity keeps bytes and decode aligned with kernel mappings" {
    for (fixtures.variant_decode_cases) |case| {
        try expectDecode(.{
            .input = case.input,
            .expected = case.expected,
            .padding = case.padding,
            .variant = fixtureVariant(case.variant_name),
        });
    }
}

test "phase 6 base64 convenience wrappers round-trip exact std urlsafe and imap encodings" {
    try expectConvenienceWrapperRoundTrip("hi", "aGk=", true, .std);
    try expectConvenienceWrapperRoundTrip("hi", "aGk", false, .std);
    try expectConvenienceWrapperRoundTrip(&fixtures.variant_sample, "APv_f4A=", true, .urlsafe);
    try expectConvenienceWrapperRoundTrip(&fixtures.variant_sample, "APv_f4A", false, .urlsafe);
    try expectConvenienceWrapperRoundTrip(&fixtures.variant_sample, "APv,f4A=", true, .imap);
    try expectConvenienceWrapperRoundTrip(&fixtures.variant_sample, "APv,f4A", false, .imap);
}

test "phase 6 base64 convenience wrappers stay exact aliases of the generic variant paths" {
    const inputs = [_][]const u8{
        "",
        "hi",
        &fixtures.variant_sample,
    };

    inline for ([_]base64.Variant{ .std, .urlsafe, .imap }) |variant| {
        inline for ([_]bool{ true, false }) |padding| {
            for (inputs) |input| {
                try expectConvenienceWrapperAliasParity(input, padding, variant);
            }
        }
    }
}

test "phase 6 base64 convenience wrappers reject foreign alphabet tails in padded and unpadded modes" {
    try expectConvenienceVariantForeignAlphabetRejection(true);
    try expectConvenienceVariantForeignAlphabetRejection(false);
}

test "phase 6 base64 reports destination bounds before encoding" {
    var padded_buf = [_]u8{0xaa} ** 3;
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(padded_buf[0..], "f", true, .std));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa }, padded_buf[0..]);

    var unpadded_buf = [_]u8{0xbb} ** 3;
    try std.testing.expectError(base64.EncodeError.DestinationTooSmall, base64.encode(unpadded_buf[0..], "foo", false, .std));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xbb, 0xbb, 0xbb }, unpadded_buf[0..]);
}

test "phase 6 base64 reports destination bounds before decoding" {
    var padded_buf = [_]u8{0xcc} ** 1;
    try std.testing.expectError(base64.DecodeError.DestinationTooSmall, base64.decode(padded_buf[0..], "Zm8=", true, .std));
    try std.testing.expectEqualSlices(u8, &[_]u8{0xcc}, padded_buf[0..]);

    var unpadded_buf = [_]u8{0xdd} ** 2;
    try std.testing.expectError(base64.DecodeError.DestinationTooSmall, base64.decode(unpadded_buf[0..], "Zm9v", false, .std));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xdd, 0xdd }, unpadded_buf[0..]);
}
