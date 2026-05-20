const std = @import("std");
const atomic = @import("atomic");
const barrier = @import("barrier");
const mmio = @import("mmio");

test "phase3 low-level wrappers keep subtractive xor min-max atomic updates explicit before MMIO publish" {
    var state: u16 = 0x0040;

    try std.testing.expectEqual(@as(u16, 0x0040), try atomic.fetchSub(u16, &state, 0x0005, .release));
    try std.testing.expectEqual(@as(u16, 0x003B), state);

    try std.testing.expectEqual(@as(u16, 0x003B), try atomic.fetchXor(u16, &state, 0x00F0, .acq_rel));
    try std.testing.expectEqual(@as(u16, 0x00CB), state);

    try std.testing.expectEqual(@as(u16, 0x00CB), try atomic.fetchMin(u16, &state, 0x00C0, .acquire));
    try std.testing.expectEqual(@as(u16, 0x00C0), state);

    try std.testing.expectEqual(@as(u16, 0x00C0), try atomic.fetchMax(u16, &state, 0x00F1, .seq_cst));
    try std.testing.expectEqual(@as(u16, 0x00F1), state);

    try std.testing.expectError(error.InvalidRmwOrdering, atomic.fetchXor(u16, &state, 0x0001, .unordered));
    try std.testing.expectEqual(@as(u16, 0x00F1), state);

    var register: u16 = 0;
    const register_ptr: *volatile u16 = @ptrCast(&register);
    const const_register_ptr: *const volatile u16 = @ptrCast(&register);

    barrier.release();
    mmio.write(u16, register_ptr, state);
    barrier.acquire();
    try std.testing.expectEqual(@as(u16, 0x00F1), mmio.read(u16, const_register_ptr));
}
