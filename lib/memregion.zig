// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const ENOSPC: i32 = 28;
pub const EINVAL: i32 = 22;
pub const GFP = usize;
pub const default_capacity: usize = 1024;

pub fn MemRegionAllocator(comptime capacity: usize) type {
    return struct {
        const Self = @This();
        const IdSet = std.StaticBitSet(capacity);

        used: IdSet = IdSet.empty,

        pub fn init() Self {
            return .{};
        }

        pub fn reset(self: *Self) void {
            self.used = IdSet.empty;
        }

        pub fn alloc(self: *Self, _: GFP) i32 {
            var id: usize = 0;
            while (id < capacity) : (id += 1) {
                if (!self.used.isSet(id)) {
                    self.used.set(id);
                    return @intCast(id);
                }
            }
            return -ENOSPC;
        }

        pub fn free(self: *Self, id: i32) bool {
            if (id < 0) return false;
            const index: usize = @intCast(id);
            if (index >= capacity or !self.used.isSet(index)) return false;
            self.used.unset(index);
            return true;
        }

        pub fn isAllocated(self: *const Self, id: i32) bool {
            if (id < 0) return false;
            const index: usize = @intCast(id);
            return index < capacity and self.used.isSet(index);
        }

        pub fn count(self: *const Self) usize {
            return self.used.count();
        }
    };
}

pub const DefaultMemRegionAllocator = MemRegionAllocator(default_capacity);
var memregion_ids: DefaultMemRegionAllocator = DefaultMemRegionAllocator.init();

pub fn memregion_alloc(gfp: GFP) i32 {
    return memregion_ids.alloc(gfp);
}

pub fn memregion_free(id: i32) void {
    _ = memregion_ids.free(id);
}

pub fn memregion_free_checked(id: i32) i32 {
    return if (memregion_ids.free(id)) 0 else -EINVAL;
}

pub fn memregion_reset_for_test() void {
    memregion_ids.reset();
}

test "memregion allocator returns lowest free nonnegative ids" {
    var ids = MemRegionAllocator(8).init();

    try std.testing.expectEqual(@as(i32, 0), ids.alloc(0));
    try std.testing.expectEqual(@as(i32, 1), ids.alloc(0));
    try std.testing.expectEqual(@as(i32, 2), ids.alloc(0));
    try std.testing.expectEqual(@as(usize, 3), ids.count());
}

test "memregion allocator reuses freed ids" {
    var ids = MemRegionAllocator(4).init();

    const a = ids.alloc(0);
    const b = ids.alloc(0);
    const c = ids.alloc(0);

    try std.testing.expect(ids.free(b));
    try std.testing.expectEqual(b, ids.alloc(0));
    try std.testing.expectEqual(@as(i32, 3), ids.alloc(0));
    try std.testing.expectEqual(@as(i32, -ENOSPC), ids.alloc(0));

    try std.testing.expect(ids.free(a));
    try std.testing.expect(ids.free(c));
    try std.testing.expectEqual(a, ids.alloc(0));
    try std.testing.expectEqual(c, ids.alloc(0));
}

test "memregion allocator rejects invalid frees defensively" {
    var ids = MemRegionAllocator(2).init();

    try std.testing.expect(!ids.free(-1));
    try std.testing.expect(!ids.free(0));

    const id = ids.alloc(0);
    try std.testing.expect(ids.isAllocated(id));
    try std.testing.expect(ids.free(id));
    try std.testing.expect(!ids.isAllocated(id));
    try std.testing.expect(!ids.free(id));
}

test "memregion module wrappers reuse the global ida-style pool" {
    memregion_reset_for_test();

    try std.testing.expectEqual(@as(i32, 0), memregion_alloc(0));
    try std.testing.expectEqual(@as(i32, 1), memregion_alloc(0));
    memregion_free(0);
    try std.testing.expectEqual(@as(i32, 0), memregion_alloc(0));
    try std.testing.expectEqual(@as(i32, -EINVAL), memregion_free_checked(99));

    memregion_reset_for_test();
}
