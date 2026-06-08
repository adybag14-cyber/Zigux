const std = @import("std");
const testing = std.testing;

const atomic = @import("atomic_helpers");

test "atomic bitwise RMW wrappers publish old values and bit mutations" {
    var or_value: u16 = 0x0104;
    try testing.expectEqual(@as(u16, 0x0104), try atomic.fetchOr(u16, &or_value, 0x0018, .release));
    try testing.expectEqual(@as(u16, 0x011C), or_value);
    try testing.expectEqual(@as(u16, 0x011C), try atomic.fetchOr(u16, &or_value, 0x8000, .acq_rel));
    try testing.expectEqual(@as(u16, 0x811C), or_value);

    var and_value: u16 = 0xFF3C;
    try testing.expectEqual(@as(u16, 0xFF3C), try atomic.fetchAnd(u16, &and_value, 0x0F3F, .acquire));
    try testing.expectEqual(@as(u16, 0x0F3C), and_value);
    try testing.expectEqual(@as(u16, 0x0F3C), try atomic.fetchAnd(u16, &and_value, 0x00FF, .seq_cst));
    try testing.expectEqual(@as(u16, 0x003C), and_value);
}

test "atomic XOR and NAND wrappers keep complement semantics explicit" {
    var xor_value: u16 = 0x0F3C;
    try testing.expectEqual(@as(u16, 0x0F3C), try atomic.fetchXor(u16, &xor_value, 0x00FF, .release));
    try testing.expectEqual(@as(u16, 0x0FC3), xor_value);
    try testing.expectEqual(@as(u16, 0x0FC3), try atomic.fetchXor(u16, &xor_value, 0x0F00, .acq_rel));
    try testing.expectEqual(@as(u16, 0x00C3), xor_value);

    var nand_value: u8 = 0b1111_0000;
    try testing.expectEqual(@as(u8, 0b1111_0000), try atomic.fetchNand(u8, &nand_value, 0b1100_1100, .seq_cst));
    try testing.expectEqual(@as(u8, 0b0011_1111), nand_value);
    try testing.expectEqual(@as(u8, 0b0011_1111), try atomic.fetchNand(u8, &nand_value, 0b0000_1111, .monotonic));
    try testing.expectEqual(@as(u8, 0b1111_0000), nand_value);
}

test "atomic bitwise RMW wrappers reject unordered operations without side effects" {
    var or_value: u16 = 0x811C;
    try testing.expectError(error.InvalidRmwOrdering, atomic.fetchOr(u16, &or_value, 0x0001, .unordered));
    try testing.expectEqual(@as(u16, 0x811C), or_value);

    var and_value: u16 = 0x003C;
    try testing.expectError(error.InvalidRmwOrdering, atomic.fetchAnd(u16, &and_value, 0x000F, .unordered));
    try testing.expectEqual(@as(u16, 0x003C), and_value);

    var xor_value: u16 = 0x00C3;
    try testing.expectError(error.InvalidRmwOrdering, atomic.fetchXor(u16, &xor_value, 0x000F, .unordered));
    try testing.expectEqual(@as(u16, 0x00C3), xor_value);

    var nand_value: u8 = 0b1111_0000;
    try testing.expectError(error.InvalidRmwOrdering, atomic.fetchNand(u8, &nand_value, 0b1111_1111, .unordered));
    try testing.expectEqual(@as(u8, 0b1111_0000), nand_value);
}

test "atomic bitwise RMW wrappers share the public RMW ordering contract" {
    const allowed = [_]atomic.Ordering{ .monotonic, .acquire, .release, .acq_rel, .seq_cst };
    for (allowed) |order| {
        try testing.expect(atomic.rmwOrderAllowed(order));
    }

    try testing.expect(!atomic.rmwOrderAllowed(.unordered));
    try testing.expectError(error.InvalidRmwOrdering, atomic.validateRmwOrder(.unordered));
}
