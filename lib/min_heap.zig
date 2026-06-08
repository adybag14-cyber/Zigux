// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub fn MinHeap(comptime T: type, comptime less: fn (T, T) bool) type {
    return struct {
        const Self = @This();

        data: []T,
        nr: usize = 0,

        pub fn init(buffer: []T) Self {
            return .{ .data = buffer, .nr = 0 };
        }

        pub fn initFull(buffer: []T) Self {
            var heap = Self{ .data = buffer, .nr = buffer.len };
            heap.heapifyAll();
            return heap;
        }

        pub fn len(self: Self) usize {
            return self.nr;
        }

        pub fn capacity(self: Self) usize {
            return self.data.len;
        }

        pub fn full(self: Self) bool {
            return self.nr == self.data.len;
        }

        pub fn peek(self: Self) ?T {
            return if (self.nr == 0) null else self.data[0];
        }

        pub fn push(self: *Self, value: T) bool {
            if (self.full()) return false;
            self.data[self.nr] = value;
            self.nr += 1;
            self.siftUp(self.nr - 1);
            return true;
        }

        pub fn pop(self: *Self) ?T {
            if (self.nr == 0) return null;

            const root = self.data[0];
            self.nr -= 1;
            if (self.nr != 0) {
                self.data[0] = self.data[self.nr];
                self.siftDown(0);
            }
            return root;
        }

        pub fn popPush(self: *Self, value: T) ?T {
            if (self.nr == 0) return null;

            const root = self.data[0];
            self.data[0] = value;
            self.siftDown(0);
            return root;
        }

        pub fn del(self: *Self, index: usize) ?T {
            if (index >= self.nr) return null;

            const removed = self.data[index];
            self.nr -= 1;
            if (index == self.nr) return removed;

            self.data[index] = self.data[self.nr];
            if (index > 0 and less(self.data[index], self.data[(index - 1) / 2])) {
                self.siftUp(index);
            } else {
                self.siftDown(index);
            }
            return removed;
        }

        pub fn heapifyAll(self: *Self) void {
            if (self.nr < 2) return;

            var i = self.nr / 2;
            while (i > 0) {
                i -= 1;
                self.siftDown(i);
            }
        }

        pub fn siftDown(self: *Self, start: usize) void {
            if (start >= self.nr) return;

            var pos = start;
            while (true) {
                const left = pos * 2 + 1;
                if (left >= self.nr) break;

                const right = left + 1;
                var child = left;
                if (right < self.nr and less(self.data[right], self.data[left])) {
                    child = right;
                }

                if (!less(self.data[child], self.data[pos])) break;
                self.swap(pos, child);
                pos = child;
            }
        }

        pub fn siftUp(self: *Self, start: usize) void {
            if (start >= self.nr) return;

            var pos = start;
            while (pos > 0) {
                const parent = (pos - 1) / 2;
                if (!less(self.data[pos], self.data[parent])) break;
                self.swap(pos, parent);
                pos = parent;
            }
        }

        fn swap(self: *Self, a: usize, b: usize) void {
            std.mem.swap(T, &self.data[a], &self.data[b]);
        }
    };
}

fn lessU32(a: u32, b: u32) bool {
    return a < b;
}

test "min heap push and pop return sorted order" {
    var buf: [8]u32 = undefined;
    var heap = MinHeap(u32, lessU32).init(buf[0..]);

    for ([_]u32{ 5, 1, 4, 2, 3 }) |value| {
        try std.testing.expect(heap.push(value));
    }

    for ([_]u32{ 1, 2, 3, 4, 5 }) |want| {
        try std.testing.expectEqual(want, heap.pop().?);
    }
    try std.testing.expectEqual(@as(?u32, null), heap.pop());
}

test "min heap full tracks capacity" {
    var buf: [2]u32 = undefined;
    var heap = MinHeap(u32, lessU32).init(buf[0..]);

    try std.testing.expect(!heap.full());
    try std.testing.expect(heap.push(2));
    try std.testing.expect(!heap.full());
    try std.testing.expect(heap.push(1));
    try std.testing.expect(heap.full());
    try std.testing.expect(!heap.push(0));
    try std.testing.expectEqual(@as(usize, 2), heap.capacity());
}

test "min heap delete index maintains heap order" {
    var buf: [8]u32 = undefined;
    var heap = MinHeap(u32, lessU32).init(buf[0..]);

    for ([_]u32{ 9, 4, 7, 1, 6, 2, 8 }) |value| {
        try std.testing.expect(heap.push(value));
    }

    const removed = heap.del(2).?;
    var last: ?u32 = null;
    while (heap.pop()) |value| {
        try std.testing.expect(value != removed);
        if (last) |prev| try std.testing.expect(prev <= value);
        last = value;
    }
}

test "min heap popPush replaces root and preserves length" {
    var buf: [8]u32 = undefined;
    var heap = MinHeap(u32, lessU32).init(buf[0..]);

    for ([_]u32{ 1, 3, 5, 7 }) |value| {
        try std.testing.expect(heap.push(value));
    }

    try std.testing.expectEqual(@as(?u32, 1), heap.popPush(4));
    try std.testing.expectEqual(@as(usize, 4), heap.len());
    try std.testing.expectEqual(@as(?u32, 3), heap.peek());

    for ([_]u32{ 3, 4, 5, 7 }) |want| {
        try std.testing.expectEqual(want, heap.pop().?);
    }
}

test "min heap can heapify an existing buffer" {
    var buf = [_]u32{ 10, 4, 7, 1, 3, 9 };
    var heap = MinHeap(u32, lessU32).initFull(buf[0..]);

    for ([_]u32{ 1, 3, 4, 7, 9, 10 }) |want| {
        try std.testing.expectEqual(want, heap.pop().?);
    }
}
