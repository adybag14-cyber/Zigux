// SPDX-License-Identifier: GPL-2.0
const std = @import("std");
const builtin = @import("builtin");

pub const EOVERFLOW: i32 = -1;

pub const SeqBuf = struct {
    buffer: []u8,
    len: usize = 0,

    pub fn init(buffer: []u8) SeqBuf {
        var seq = SeqBuf{ .buffer = buffer };
        seq.clear();
        return seq;
    }

    pub fn clear(self: *SeqBuf) void {
        self.len = 0;
        if (self.buffer.len != 0) self.buffer[0] = 0;
    }

    pub fn hasOverflowed(self: *const SeqBuf) bool {
        return self.len > self.buffer.len;
    }

    pub fn setOverflow(self: *SeqBuf) void {
        self.len = self.buffer.len + 1;
    }

    pub fn bufferLeft(self: *const SeqBuf) usize {
        if (self.hasOverflowed()) return 0;
        return self.buffer.len - self.len;
    }

    pub fn used(self: *const SeqBuf) usize {
        return @min(self.len, self.buffer.len);
    }

    pub fn str(self: *SeqBuf) []const u8 {
        if (self.buffer.len == 0) return "";
        if (self.bufferLeft() != 0) {
            self.buffer[self.len] = 0;
            return self.buffer[0..self.len];
        }
        self.buffer[self.buffer.len - 1] = 0;
        return self.buffer[0 .. self.buffer.len - 1];
    }

    pub fn getBuf(self: *SeqBuf) ?[]u8 {
        if (self.len < self.buffer.len) return self.buffer[self.len..];
        return null;
    }

    pub fn commit(self: *SeqBuf, num: isize) void {
        if (num < 0) {
            self.setOverflow();
            return;
        }

        const count: usize = @intCast(num);
        if (self.len + count > self.buffer.len) {
            self.setOverflow();
            return;
        }
        self.len += count;
    }

    pub fn pop(self: *SeqBuf) i32 {
        if (self.len == 0 or self.hasOverflowed()) return -1;
        self.len -= 1;
        return self.buffer[self.len];
    }

    pub fn puts(self: *SeqBuf, text: []const u8) i32 {
        const needed = text.len + 1;
        if (!self.canFit(needed)) {
            self.setOverflow();
            return EOVERFLOW;
        }

        @memcpy(self.buffer[self.len .. self.len + text.len], text);
        self.buffer[self.len + text.len] = 0;
        self.len += text.len;
        return 0;
    }

    pub fn putc(self: *SeqBuf, c: u8) i32 {
        if (!self.canFit(1)) {
            self.setOverflow();
            return EOVERFLOW;
        }

        self.buffer[self.len] = c;
        self.len += 1;
        return 0;
    }

    pub fn putmem(self: *SeqBuf, mem: []const u8) i32 {
        if (!self.canFit(mem.len)) {
            self.setOverflow();
            return EOVERFLOW;
        }

        @memcpy(self.buffer[self.len .. self.len + mem.len], mem);
        self.len += mem.len;
        return 0;
    }

    pub fn putmemHex(self: *SeqBuf, mem: []const u8) i32 {
        const max_memhex_bytes = 8;
        var offset: usize = 0;

        while (offset < mem.len) {
            const chunk_len = @min(max_memhex_bytes, mem.len - offset);
            var hex: [max_memhex_bytes * 2 + 1]u8 = undefined;
            var out: usize = 0;

            if (builtin.target.cpu.arch.endian() == .big) {
                var i: usize = 0;
                while (i < chunk_len) : (i += 1) {
                    appendHexByte(&hex, &out, mem[offset + i]);
                }
            } else {
                var i = chunk_len;
                while (i > 0) {
                    i -= 1;
                    appendHexByte(&hex, &out, mem[offset + i]);
                }
            }

            hex[out] = ' ';
            out += 1;
            if (self.putmem(hex[0..out]) != 0) return EOVERFLOW;
            offset += chunk_len;
        }
        return 0;
    }

    pub fn printf(self: *SeqBuf, comptime fmt: []const u8, args: anytype) i32 {
        if (self.len >= self.buffer.len) {
            self.setOverflow();
            return EOVERFLOW;
        }

        const available = self.buffer[self.len..];
        const written = std.fmt.bufPrint(available, fmt, args) catch {
            self.setOverflow();
            return EOVERFLOW;
        };

        if (self.len + written.len >= self.buffer.len) {
            self.setOverflow();
            return EOVERFLOW;
        }

        self.len += written.len;
        self.buffer[self.len] = 0;
        return 0;
    }

    fn canFit(self: *const SeqBuf, count: usize) bool {
        return !self.hasOverflowed() and count <= self.buffer.len - self.len;
    }
};

pub fn seq_buf_init(seq: *SeqBuf, buffer: []u8) void {
    seq.* = SeqBuf.init(buffer);
}

pub fn seq_buf_clear(seq: *SeqBuf) void {
    seq.clear();
}

pub fn seq_buf_has_overflowed(seq: *const SeqBuf) bool {
    return seq.hasOverflowed();
}

pub fn seq_buf_set_overflow(seq: *SeqBuf) void {
    seq.setOverflow();
}

pub fn seq_buf_buffer_left(seq: *const SeqBuf) usize {
    return seq.bufferLeft();
}

pub fn seq_buf_used(seq: *const SeqBuf) usize {
    return seq.used();
}

pub fn seq_buf_str(seq: *SeqBuf) []const u8 {
    return seq.str();
}

pub fn seq_buf_get_buf(seq: *SeqBuf) ?[]u8 {
    return seq.getBuf();
}

pub fn seq_buf_commit(seq: *SeqBuf, num: isize) void {
    seq.commit(num);
}

pub fn seq_buf_pop(seq: *SeqBuf) i32 {
    return seq.pop();
}

pub fn seq_buf_puts(seq: *SeqBuf, text: []const u8) i32 {
    return seq.puts(text);
}

pub fn seq_buf_putc(seq: *SeqBuf, c: u8) i32 {
    return seq.putc(c);
}

pub fn seq_buf_putmem(seq: *SeqBuf, mem: []const u8) i32 {
    return seq.putmem(mem);
}

pub fn seq_buf_putmem_hex(seq: *SeqBuf, mem: []const u8) i32 {
    return seq.putmemHex(mem);
}

fn appendHexByte(hex: []u8, out: *usize, byte: u8) void {
    const digits = "0123456789abcdef";
    hex[out.*] = digits[byte >> 4];
    hex[out.* + 1] = digits[byte & 0x0f];
    out.* += 2;
}

test "seq buf init clear puts putc and string termination" {
    var storage = [_]u8{ 9, 9, 9, 9, 9, 9, 9, 9 };
    var seq = SeqBuf.init(storage[0..]);

    try std.testing.expectEqual(@as(usize, 0), seq.len);
    try std.testing.expectEqual(@as(u8, 0), storage[0]);
    try std.testing.expectEqual(@as(i32, 0), seq_buf_puts(&seq, "ab"));
    try std.testing.expectEqual(@as(i32, 0), seq_buf_putc(&seq, 'c'));
    try std.testing.expectEqualStrings("abc", seq_buf_str(&seq));

    seq_buf_clear(&seq);
    try std.testing.expectEqualStrings("", seq_buf_str(&seq));
}

test "seq buf puts reserves a trailing nul byte" {
    var storage = [_]u8{ 0, 0, 0, 0 };
    var seq = SeqBuf.init(storage[0..]);

    try std.testing.expectEqual(@as(i32, 0), seq.puts("abc"));
    try std.testing.expectEqual(@as(i32, EOVERFLOW), seq.puts("d"));
    try std.testing.expect(seq.hasOverflowed());
    try std.testing.expectEqualStrings("abc", seq.str());
}

test "seq buf raw memory can fill the full buffer" {
    var storage = [_]u8{ 0, 0, 0, 0 };
    var seq = SeqBuf.init(storage[0..]);

    try std.testing.expectEqual(@as(i32, 0), seq.putmem("abcd"));
    try std.testing.expectEqual(@as(usize, 4), seq.used());
    try std.testing.expectEqualStrings("abc", seq.str());
}

test "seq buf get buffer commit and pop" {
    var storage = [_]u8{ 0, 0, 0, 0, 0 };
    var seq = SeqBuf.init(storage[0..]);

    const tail = seq.getBuf().?;
    @memcpy(tail[0..2], "xy");
    seq.commit(2);
    try std.testing.expectEqualStrings("xy", seq.str());
    try std.testing.expectEqual(@as(i32, 'y'), seq.pop());
    try std.testing.expectEqualStrings("x", seq.str());

    seq.commit(-1);
    try std.testing.expect(seq.hasOverflowed());
}

test "seq buf putmem hex follows native endian chunk order" {
    var storage = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    var seq = SeqBuf.init(storage[0..]);

    try std.testing.expectEqual(@as(i32, 0), seq.putmemHex(&.{ 0x12, 0x34, 0xab, 0xcd }));
    if (builtin.target.cpu.arch.endian() == .big) {
        try std.testing.expectEqualStrings("1234abcd ", seq.str());
    } else {
        try std.testing.expectEqualStrings("cdab3412 ", seq.str());
    }
}

test "seq buf printf-like append reserves nul byte" {
    var storage = [_]u8{ 0, 0, 0, 0, 0, 0, 0, 0 };
    var seq = SeqBuf.init(storage[0..]);

    try std.testing.expectEqual(@as(i32, 0), seq.printf("{}-{x}", .{ 5, 255 }));
    try std.testing.expectEqualStrings("5-ff", seq.str());

    var tiny = [_]u8{ 0, 0, 0, 0 };
    var small = SeqBuf.init(tiny[0..]);
    try std.testing.expectEqual(@as(i32, EOVERFLOW), small.printf("abcd", .{}));
}
