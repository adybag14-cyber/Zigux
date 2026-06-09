const std = @import("std");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const Fixture = struct {
    find_bit: struct {
        bits_per_long: usize,
        inclusive_boundary_next: usize,
        inclusive_boundary_zero: usize,
        inclusive_boundary_and: usize,
        tail_andnot_clamped_first: usize,
        tail_andnot_clamped_next: usize,
        tail_andnot_clamped_exhausted: usize,
        tail_inclusive_boundary_next: usize,
        tail_inclusive_boundary_zero: usize,
        tail_inclusive_boundary_and: usize,
        tail_clump_first: usize,
        tail_clump_first_value: u8,
        tail_clump_next: usize,
        tail_clump_next_value: u8,
        tail_clump_exhausted: usize,
        tail_clump_exhausted_value: u8,
    },
    bitmap: struct {
        copy_values: []const u64,
        copy_clear_tail_values: []const u64,
        copy_and_extend_values: []const u64,
        complement_values: []const u64,
        partial_xor_nbits: usize,
        partial_xor_masked_values: []const u64,
    },
    cmdline: struct {
        signed_k: struct {
            value: u64,
            rest: []const u8,
        },
        signed_hex_k: struct {
            value: u64,
            rest: []const u8,
        },
        signed_octal_m: struct {
            value: u64,
            rest: []const u8,
        },
        saturated_positive_signed: struct {
            value: u64,
            rest: []const u8,
        },
        first_arg: struct {
            param: []const u8,
            value: []const u8,
            remaining: []const u8,
        },
        second_arg: struct {
            param: []const u8,
            value: []const u8,
            remaining: []const u8,
        },
        quoted_arg: struct {
            param: []const u8,
            value: []const u8,
            remaining: []const u8,
        },
        empty_quoted_arg: struct {
            param: []const u8,
            value: []const u8,
            remaining: []const u8,
        },
        unterminated_arg: struct {
            param: []const u8,
            value: []const u8,
            remaining: []const u8,
        },
    },
    ctype: struct {
        w8_marker: ?u8 = null,
    },
    hweight: struct {
        w8: u8,
        w16: u8,
    },
    rbtree: struct {
        cached_leftmost_return_serials: []const i32,
        cached_root_transition_serials: []const i32,
    },
    slab: struct {
        null_without_reclaim: bool,
        array_zeroed: bool,
        alloc_count_after_kmalloc_array: isize,
        alloc_count_after_kmalloc_array_free: isize,
        slab_is_available: bool,
    },
    str_error_r: struct {
        tiny_unknown: []const u8,
    },
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

test "phase1 helpers fixture keeps expanded find-bit boundary schema" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    try std.testing.expectEqual(@as(usize, 64), fixture.find_bit.bits_per_long);
    try std.testing.expectEqual(@as(usize, 63), fixture.find_bit.inclusive_boundary_next);
    try std.testing.expectEqual(fixture.find_bit.inclusive_boundary_next, fixture.find_bit.inclusive_boundary_zero);
    try std.testing.expectEqual(fixture.find_bit.inclusive_boundary_next, fixture.find_bit.inclusive_boundary_and);

    try std.testing.expectEqual(@as(usize, 67), fixture.find_bit.tail_andnot_clamped_first);
    try std.testing.expectEqual(@as(usize, 67), fixture.find_bit.tail_andnot_clamped_next);
    try std.testing.expectEqual(@as(usize, 69), fixture.find_bit.tail_andnot_clamped_exhausted);

    try std.testing.expectEqual(@as(usize, 68), fixture.find_bit.tail_inclusive_boundary_next);
    try std.testing.expectEqual(fixture.find_bit.tail_inclusive_boundary_next, fixture.find_bit.tail_inclusive_boundary_zero);
    try std.testing.expectEqual(fixture.find_bit.tail_inclusive_boundary_next, fixture.find_bit.tail_inclusive_boundary_and);

    try std.testing.expectEqual(@as(usize, 64), fixture.find_bit.tail_clump_first);
    try std.testing.expectEqual(@as(u8, 8), fixture.find_bit.tail_clump_first_value);
    try std.testing.expectEqual(@as(usize, 64), fixture.find_bit.tail_clump_next);
    try std.testing.expectEqual(@as(u8, 8), fixture.find_bit.tail_clump_next_value);
    try std.testing.expectEqual(@as(usize, 69), fixture.find_bit.tail_clump_exhausted);
    try std.testing.expectEqual(@as(u8, 90), fixture.find_bit.tail_clump_exhausted_value);
}

test "phase1 helpers fixture preserves widened helper sections" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    try std.testing.expectEqualSlices(u64, &.{ 18446744073709551615, 18446744073709551615 }, fixture.bitmap.copy_values);
    try std.testing.expectEqualSlices(u64, &.{ 18446744073709551615, 31 }, fixture.bitmap.copy_clear_tail_values);
    try std.testing.expectEqualSlices(u64, &.{ 18446744073709551615, 31, 0 }, fixture.bitmap.copy_and_extend_values);
    try std.testing.expectEqualSlices(u64, &.{ 18446744073709551605, 29 }, fixture.bitmap.complement_values);
    try std.testing.expectEqual(@as(usize, 4), fixture.bitmap.partial_xor_nbits);
    try std.testing.expectEqualSlices(u64, &.{14}, fixture.bitmap.partial_xor_masked_values);

    try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, fixture.rbtree.cached_leftmost_return_serials);
    try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, fixture.rbtree.cached_root_transition_serials);

    try std.testing.expect(fixture.slab.null_without_reclaim);
    try std.testing.expect(fixture.slab.array_zeroed);
    try std.testing.expect(fixture.slab.slab_is_available);
    try std.testing.expectEqual(@as(isize, 1), fixture.slab.alloc_count_after_kmalloc_array);
    try std.testing.expectEqual(@as(isize, 0), fixture.slab.alloc_count_after_kmalloc_array_free);
    try std.testing.expectEqualStrings("INTERNA", fixture.str_error_r.tiny_unknown);

    try std.testing.expectEqual(@as(u8, 4), fixture.hweight.w8);
    try std.testing.expectEqual(@as(u8, 8), fixture.hweight.w16);
}

test "phase1 helpers fixture keeps cmdline signed and quoting contract data" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    try std.testing.expectEqual(@as(u64, 18446744073709549568), fixture.cmdline.signed_k.value);
    try std.testing.expectEqualStrings(" tail", fixture.cmdline.signed_k.rest);
    try std.testing.expectEqual(@as(u64, 18446744073709549568), fixture.cmdline.signed_hex_k.value);
    try std.testing.expectEqualStrings("tail", fixture.cmdline.signed_hex_k.rest);
    try std.testing.expectEqual(@as(u64, 8388608), fixture.cmdline.signed_octal_m.value);
    try std.testing.expectEqualStrings("more", fixture.cmdline.signed_octal_m.rest);
    try std.testing.expectEqual(@as(u64, 9223372036854775807), fixture.cmdline.saturated_positive_signed.value);

    try std.testing.expectEqualStrings("console", fixture.cmdline.first_arg.param);
    try std.testing.expectEqualStrings("ttyS0,115200", fixture.cmdline.first_arg.value);
    try std.testing.expectEqualStrings("root=\"/dev/sda1 quiet\" panic=-1", fixture.cmdline.first_arg.remaining);
    try std.testing.expectEqualStrings("root", fixture.cmdline.second_arg.param);
    try std.testing.expectEqualStrings("/dev/sda1 quiet", fixture.cmdline.second_arg.value);
    try std.testing.expectEqualStrings("panic=-1", fixture.cmdline.second_arg.remaining);
    try std.testing.expectEqualStrings("mode", fixture.cmdline.quoted_arg.param);
    try std.testing.expectEqualStrings("fast path", fixture.cmdline.quoted_arg.value);
    try std.testing.expectEqualStrings("tail", fixture.cmdline.quoted_arg.remaining);
    try std.testing.expectEqualStrings("", fixture.cmdline.empty_quoted_arg.value);
    try std.testing.expectEqualStrings("fast boot", fixture.cmdline.unterminated_arg.value);
}
